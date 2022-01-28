import csv
import json
import logging
from io import StringIO

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import ModelAdmin, register
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from admin_extra_urls.api import ExtraUrlMixin, button, url
from admin_extra_urls.utils import labelize
from adminfilters.autocomplete import AutoCompleteFilter
from import_export import fields
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import LinkedObjectsMixin

from ..account.models import User
from ..administration.widgets import JsonWidget
from ..utils.security import is_root
from .forms import (
    RuleDownloadCSVFileProcessForm,
    RuleFileProcessForm,
    RuleForm,
    RuleTestForm,
)
from .models import MONITORED_FIELDS, Rule, RuleCommit
from .security import clean_context

logger = logging.getLogger(__name__)


class AutocompleteWidget(forms.Widget):
    template_name = "steficon/widgets/autocomplete.html"
    # template_name = 'django/forms/widgets/select.html'

    url_name = "%s:%s_%s_autocomplete"

    def __init__(self, model, admin_site, attrs=None, choices=(), using=None):
        self.model = model
        self.admin_site = admin_site
        self.db = using
        self.choices = choices
        self.attrs = {} if attrs is None else attrs.copy()

    def get_url(self):
        model = self.model
        return reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name))

    def get_context(self, name, value, attrs):
        context = {}
        context["widget"] = {
            "query_string": "",
            "lookup_kwarg": "term",
            "url": self.get_url(),
            "target_opts": {"app_label": "", "model_name": "", "target_field": ""},
            "name": name,
            "media": self.media,
            "is_hidden": self.is_hidden,
            "required": self.is_required,
            "value": self.format_value(value),
            "attrs": self.build_attrs(self.attrs, attrs),
            "template_name": self.template_name,
        }
        return context

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = ("admin/js/vendor/select2/i18n/%s.js" % i18n_name,) if i18n_name else ()
        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery%s.js" % extra,
                "admin/js/vendor/select2/select2.full%s.js" % extra,
            )
            + i18n_file
            + (
                "admin/js/jquery.init.js",
                "admin/js/autocomplete.js",
                "adminfilters/adminfilters%s.js" % extra,
            ),
            css={
                "screen": (
                    "admin/css/vendor/select2/select2%s.css" % extra,
                    "adminfilters/adminfilters.css",
                ),
            },
        )


class TestRuleMixin:
    @button(visible=lambda o, r: "/test/" not in r.path)
    def test(self, request, pk):
        rule: Rule = self.get_object(request, pk)
        context = self.get_common_context(
            request,
            pk,
            title=f"{rule}",
            state_opts=RuleCommit._meta,
        )

        if request.method == "POST":
            form = RuleTestForm(request.POST, request.FILES)
            if form.is_valid():
                selection = form.cleaned_data["opt"]
                if selection == "optFile":
                    data = form.cleaned_data.get("file")
                    title = f"Test result for '{rule}' using file"
                elif selection == "optData":
                    data = form.cleaned_data.get("raw_data")
                    title = f"Test result for '{rule}' using sample data"
                elif selection == "optTargetPopulation":
                    tp = form.cleaned_data.get("target_population")
                    context["target_population"] = tp
                    data = [{"household": e.household} for e in tp.selections.all()]
                    title = f"Test result for '{rule}' using TargetPopulation '{tp}'"
                elif selection == "optContentType":
                    ct: ContentType = form.cleaned_data["content_type"]
                    filters = json.loads(form.cleaned_data.get("content_type_filters") or "{}")
                    qs = ct.model_class().objects.filter(**filters)
                    data = qs.all()
                    title = f"Test result for '{rule}' using ContentType '{ct}'"
                else:
                    raise Exception(f"Invalid option '{selection}'")
                if not isinstance(data, (list, tuple, QuerySet)):
                    data = [data]
                context["title"] = title
                context["selection"] = selection
                results = []
                for values in data:
                    row = {
                        "input": values,
                        "input_type": values.__class__.__name__,
                        "data": "",
                        "error": None,
                        "success": True,
                    }
                    try:
                        if isinstance(rule, Rule):
                            row["result"] = rule.interpreter.execute(values)
                        else:
                            row["result"] = rule.execute(values)
                    except Exception as e:
                        row["error"] = "%s: %s" % (e.__class__.__name__, str(e))
                        row["success"] = False
                    results.append(row)
                context["results"] = results
            else:
                context["form"] = form
        else:
            context["form"] = RuleTestForm(initial={"raw_data": '{"a": 1, "b":2}', "opt": "optFile"})
        if "form" in context:
            from hct_mis_api.apps.targeting.models import TargetPopulation

            context["form"].fields["target_population"].widget = AutocompleteWidget(TargetPopulation, self.admin_site)
            context["form"].fields["content_type"].widget = AutocompleteWidget(ContentType, self.admin_site)
        return TemplateResponse(request, "admin/steficon/rule/test.html", context)


class RuleResource(ModelResource):
    created_by = fields.Field(
        column_name="created_by", attribute="created_by", widget=ForeignKeyWidget(User, "username")
    )

    updated_by = fields.Field(
        column_name="updated_by", attribute="created_by", widget=ForeignKeyWidget(User, "username")
    )

    class Meta:
        model = Rule
        fields = (
            "name",
            "version",
            "definition",
            "enabled",
            "deprecated",
            "language",
            "security",
            "created_by",
            "updated_by",
        )
        import_id_fields = ("name",)


@register(Rule)
class RuleAdmin(ExtraUrlMixin, ImportExportMixin, TestRuleMixin, LinkedObjectsMixin, ModelAdmin):
    list_display = ("name", "version", "language", "enabled", "deprecated", "created_by", "updated_by", "stable")
    list_filter = ("language", "enabled", "deprecated")
    search_fields = ("name",)
    form = RuleForm
    readonly_fields = (
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "version",
    )
    change_form_template = None
    change_list_template = None
    resource_class = RuleResource
    fieldsets = [
        (
            None,
            {
                "fields": (
                    ("name", "version"),
                    ("enabled", "deprecated"),
                )
            },
        ),
        (
            "code",
            {
                "classes": ("collapse", "open"),
                "fields": (
                    "language",
                    "definition",
                ),
            },
        ),
        (
            "Info",
            {
                "classes": ["collapse"],
                "fields": ("description", "flags"),
            },
        ),
        (
            "Data",
            {
                "classes": ("collapse",),
                "fields": (
                    ("created_by", "created_at"),
                    ("updated_by", "updated_at"),
                ),
            },
        ),
    ]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "flags":
            if is_root(request):
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return is_root(request)

    def has_change_permission(self, request, obj=None):
        return is_root(request)

    def get_ignored_linked_objects(self):
        return ["history"]

    def get_form(self, request, obj=None, change=False, **kwargs):
        return super().get_form(request, obj, change, **kwargs)

    def stable(self, obj):
        try:
            url = reverse("admin:steficon_rulecommit_change", args=[obj.latest.pk])
            return mark_safe(f'<a href="{url}">{obj.latest.version}</a>')
        except (RuleCommit.DoesNotExist, AttributeError):
            pass

    def delete_view(self, request, object_id, extra_context=None):
        return super().delete_view(request, object_id, extra_context)

    def render_delete_form(self, request, context):
        return super().render_delete_form(request, context)

    def _get_csv_config(self, form):
        return dict(
            quoting=int(form.cleaned_data["quoting"]),
            delimiter=form.cleaned_data["delimiter"],
            quotechar=form.cleaned_data["quotechar"],
            escapechar=form.cleaned_data["escapechar"],
        )

    @button(visible=lambda c: "/change/" in c["request"].path)
    def process_file(self, request, pk):
        context = self.get_common_context(
            request,
            pk,
            step=1,
            title="Process CSV file",
            state_opts=RuleCommit._meta,
        )
        if request.method == "POST":
            rule: Rule = self.get_object(request, pk)
            if request.POST["step"] == "1":
                form = RuleFileProcessForm(request.POST, request.FILES)
                if form.is_valid():
                    csv_config = self._get_csv_config(form)
                    f = request.FILES["file"]
                    input = f.read().decode("utf-8")
                    data = csv.DictReader(StringIO(input), fieldnames=None, **csv_config)
                    context["fields"] = data.fieldnames
                    for attr in form.cleaned_data["results"]:
                        context["fields"].append(labelize(attr))
                    info_col = labelize(form.cleaned_data["results"][0])
                    results = []
                    for entry in data:
                        try:
                            result = rule.execute(entry, only_enabled=False, only_release=False)
                            for attr in form.cleaned_data["results"]:
                                entry[labelize(attr)] = getattr(result, attr, "<ATTR NOT FOUND>")
                        except Exception as e:
                            entry[info_col] = str(e)
                        results.append(entry)
                    context["results"] = results
                    context["step"] = 2
                    context["form"] = RuleDownloadCSVFileProcessForm(
                        initial={
                            "quoting": csv_config["quoting"],
                            "delimiter": csv_config["delimiter"],
                            "quotechar": csv_config["quotechar"],
                            "escapechar": csv_config["escapechar"],
                            "data": json.dumps(results),
                            "fields": ",".join(context["fields"]),
                            "filename": f.name,
                        }
                    )
                else:
                    context["form"] = form

            elif request.POST["step"] == "2":
                form = RuleDownloadCSVFileProcessForm(request.POST)
                if form.is_valid():
                    try:
                        csv_config = self._get_csv_config(form)
                        data = form.cleaned_data["data"]
                        fields = form.cleaned_data["fields"]
                        response = HttpResponse(
                            content_type="text/csv",
                            headers={
                                "Content-Disposition": 'attachment; filename="%s"' % form.cleaned_data["filename"]
                            },
                        )

                        writer = csv.DictWriter(response, fieldnames=fields, **csv_config)
                        writer.writeheader()
                        writer.writerows(data)
                        return response
                    except Exception:
                        raise
                else:
                    context["form"] = form
        else:
            context["form"] = RuleFileProcessForm(initial={"results": "value"})

        return TemplateResponse(request, "admin/steficon/rule/file_process.html", context)

    @button(visible=lambda o, r: "/changelog/" not in r.path)
    def changelog(self, request, pk):
        context = self.get_common_context(request, pk, title="Changelog", state_opts=RuleCommit._meta)
        return TemplateResponse(request, "admin/steficon/rule/changelog.html", context)

    @url(url="<int:pk>/revert/<int:state>/")
    def do_revert(self, request, pk, state):
        try:
            self.get_object(request, pk)
            state = self.object.history.get(pk=state)
            with atomic():
                if "_restore" in request.POST:
                    state.revert()
                else:
                    state.revert(["definition"])
            url = reverse("admin:steficon_rule_change", args=[self.object.id])
            return HttpResponseRedirect(url)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

    @button(visible=lambda c: "/change/" in c["request"].path)
    def diff(self, request, pk):
        try:
            context = self.get_common_context(request, pk, action="Code history")
            state_pk = request.GET.get("state_pk")
            if state_pk:
                state = self.object.history.get(pk=state_pk)
            else:
                state = self.object.history.first()

            context["state"] = state
            context["title"] = (
                f"Change #{state.version} on " f"{state.timestamp.strftime('%d, %b %Y at %H:%M')} by {state.updated_by}"
            )
            return TemplateResponse(request, "admin/steficon/rule/diff.html", context)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {e}", messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return super().change_view(request, object_id, form_url, extra_context)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        if request.method == "POST" and "_release" in request.POST:
            object_id = None
        return super()._changeform_view(request, object_id, form_url, extra_context)

    @atomic()
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()


class RuleCommitResource(ModelResource):
    rule = fields.Field(column_name="rule", attribute="rule", widget=ForeignKeyWidget(Rule, "name"))
    updated_by = fields.Field(
        column_name="updated_by", attribute="created_by", widget=ForeignKeyWidget(User, "username")
    )

    class Meta:
        model = RuleCommit
        fields = ("timestamp", "rule", "version", "updated_by", "affected_fields", "is_release")
        import_id_fields = ("rule", "version")


@register(RuleCommit)
class RuleCommitAdmin(ExtraUrlMixin, ImportExportMixin, LinkedObjectsMixin, TestRuleMixin, ModelAdmin):
    list_display = ("timestamp", "rule", "version", "updated_by", "is_release", "enabled", "deprecated")
    list_filter = (("rule", AutoCompleteFilter), "is_release", "enabled", "deprecated")
    search_fields = ("name",)
    readonly_fields = ("updated_by", "rule", "affected_fields", "version", "definition")
    change_form_template = None
    change_list_template = None
    resource_class = RuleCommitResource
    fieldsets = [
        (
            None,
            {"fields": (("is_release", "enabled", "deprecated"),)},
        ),
        # (
        #     "code",
        #     {
        #         "classes": ("collapse", "open"),
        #         "fields": (
        #             "language",
        #             "definition",
        #         ),
        #     },
        # ),
        # (
        #     "Info",
        #     {
        #         "classes": ["collapse"],
        #         "fields": ("description", "flags"),
        #     },
        # ),
        # (
        #     "Data",
        #     {
        #         "classes": ("collapse",),
        #         "fields": (
        #             ("created_by", "created_at"),
        #             ("updated_by", "updated_at"),
        #         ),
        #     },
        # ),
    ]

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     self.request = request
    #     return super().render_change_form(request, context, add, change, form_url, obj)
    #
    # @property
    # def change_form_template(self):
    #     return self.request

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
