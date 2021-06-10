from datetime import datetime
from operator import itemgetter

from django import forms
from django.contrib import admin, messages
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.transaction import atomic
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.filters import TextFieldFilter

from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.erp_datahub.models import DownPayment, FundsCommitment
from hct_mis_api.apps.erp_datahub.tasks.sync_to_mis_datahub import SyncToMisDatahubTask
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.mis_datahub import models as mis_models


class NumberValidator(RegexValidator):
    regex = r"[0-9]{10,}"


class FundsCommitmentAddForm(forms.ModelForm):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects, to_field_name="code")
    currency_code = forms.ChoiceField(choices=sorted(CURRENCY_CHOICES[1:], key=itemgetter(1)))
    funds_commitment_number = forms.CharField(required=True)
    vendor_id = forms.CharField(validators=[NumberValidator, MinLengthValidator(10)])
    gl_account = forms.CharField(validators=[NumberValidator, MinLengthValidator(10)])
    business_office_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code", required=False
    )

    class Meta:
        model = FundsCommitment
        exclude = ("update_date", "updated_by", "mis_sync_flag", "mis_sync_date", "ca_sync_date", "ca_sync_flag")

    def clean_business_area(self):
        return self.cleaned_data["business_area"].code


class DownPaymentAddForm(forms.ModelForm):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects, to_field_name="code")
    business_office_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code", required=False
    )

    class Meta:
        model = DownPayment
        exclude = ("update_date", "updated_by", "mis_sync_flag", "mis_sync_date", "ca_sync_date", "ca_sync_flag")

    def clean_business_area(self):
        return self.cleaned_data["business_area"].code


class FundsCommitmentAssignBusinessOffice(forms.ModelForm):
    business_office_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code", required=True
    )

    class Meta:
        model = FundsCommitment
        fields = ("business_office_code",)

    def clean_business_office_code(self):
        return self.cleaned_data["business_office_code"].code


def should_show_assign_business_office(request, obj):
    business_area = BusinessArea.objects.get(code=obj.business_area)
    return business_area.is_split and obj.business_office_code is None


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("rec_serial_number", "business_area", "funds_commitment_number", "posting_date")
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    date_hierarchy = "create_date"
    form = FundsCommitmentAddForm

    @atomic(using="cash_assist_datahub_erp")
    @atomic(using="default")
    @button(permission=should_show_assign_business_office)
    def assign_business_office(self, request, pk):
        context = self.get_common_context(request, pk, title="Please assign business office")
        obj: FundsCommitment = context["original"]
        business_area = BusinessArea.objects.get(code=obj.business_area)
        context["business_area"] = business_area
        if request.method == "POST":
            form = FundsCommitmentAssignBusinessOffice(request.POST, instance=obj)
        else:
            form = FundsCommitmentAssignBusinessOffice(instance=obj)
        form.fields["business_office_code"] = forms.ModelChoiceField(
            queryset=BusinessArea.objects.filter(parent=business_area), to_field_name="code"
        )
        if request.method == "POST":
            if form.is_valid():
                form.save()
                obj.refresh_from_db()
                messages.success(request, "Business Office assigned, Founds Commitment sent")
                mis_funds_commitment = mis_models.FundsCommitment(**SyncToMisDatahubTask.get_model_dict(obj))
                mis_funds_commitment.business_area = obj.business_office_code
                mis_funds_commitment.save()
                obj.mis_sync_flag = True
                obj.mis_sync_date = datetime.now()
                obj.save()
                return redirect(f"/api/admin/erp_datahub/fundscommitment/{pk}/")

        context["form"] = form
        return TemplateResponse(request, "admin/erp_datahub/funds_commitment/assign_business_office.html", context)

    @button()
    def execute_exchange_rate_sync(self, request):
        if request.method == "POST":
            from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import PullFromErpDatahubTask

            task = PullFromErpDatahubTask()
            task.execute()
            self.message_user(request, "Exchange rate synced", messages.SUCCESS)
        else:
            return _confirm_action(
                self,
                request,
                self.execute_exchange_rate_sync,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>                
                        <h3>Import will only be simulated</h3> 
                        """
                ),
                "Successfully executed",
                template="admin_extra_urls/confirm.html",
            )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["created_by"] = request.user.email
        initial["updated_by"] = request.user.email
        initial["posting_date"] = timezone.now()
        initial["status_date"] = timezone.now()
        return initial

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not change:
            return FundsCommitmentAddForm
        return super().get_form(request, obj, change, **kwargs)


class DownPaymentAssignBusinessOffice(forms.ModelForm):
    business_office_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code", required=True
    )

    class Meta:
        model = DownPayment
        fields = ("business_office_code",)

    def clean_business_office_code(self):
        return self.cleaned_data["business_office_code"].code


@admin.register(DownPayment)
class DownPaymentAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    form = DownPaymentAddForm
    date_hierarchy = "create_date"

    @atomic(using="cash_assist_datahub_erp")
    @atomic(using="default")
    @button(permission=should_show_assign_business_office)
    def assign_business_office(self, request, pk):
        context = self.get_common_context(request, pk, title="Please assign business office")
        obj: DownPayment = context["original"]
        business_area = BusinessArea.objects.get(code=obj.business_area)
        context["business_area"] = business_area
        if request.method == "POST":
            form = DownPaymentAssignBusinessOffice(request.POST, instance=obj)
        else:
            form = DownPaymentAssignBusinessOffice(instance=obj)
        form.fields["business_office_code"] = forms.ModelChoiceField(
            queryset=BusinessArea.objects.filter(parent=business_area), to_field_name="code"
        )
        if request.method == "POST":
            if form.is_valid():
                form.save()
                obj.refresh_from_db()
                messages.success(request, "Business Office assigned, Founds Commitment sent")
                mis_down_payment = mis_models.DownPayment(**SyncToMisDatahubTask.get_model_dict(obj))
                mis_down_payment.business_area = obj.business_office_code
                obj.mis_sync_flag = True
                obj.mis_sync_date = datetime.now()
                obj.save()
                mis_down_payment.save()
                return redirect(f"/api/admin/erp_datahub/downpayment/{pk}/")

        context["form"] = form
        return TemplateResponse(request, "admin/erp_datahub/funds_commitment/assign_business_office.html", context)
