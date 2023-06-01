import itertools
import logging
import pickle
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from uuid import UUID

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField
from django.template import Context, Template
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import strftime
from django.utils.functional import cached_property
from django.utils.text import slugify

from natural_keys import NaturalKeyModel
from sentry_sdk import capture_exception, configure_scope

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea

from .defaults import SYSTEM_PARAMETRIZER
from .exceptions import QueryRunError
from .json import PQJSONEncoder
from .utils import dict_hash, to_dataset
from .validators import FrequencyValidator

logger = logging.getLogger(__name__)

mimetype_map = {
    "csv": "text/csv",
    "html": "text/html",
    "json": "application/json",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xml": "application/xml",
    "yaml": "text/yaml",
}

MIMETYPES = ((k, v) for k, v in mimetype_map.items())


def validate_queryargs(value: Any) -> None:
    try:
        if not isinstance(value, dict):
            raise ValidationError("QueryArgs must be a dict")
        product = list(itertools.product(*value.values()))
        [dict(zip(value.keys(), e)) for e in product]
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("%(exc)s: " "%(value)s is not a valid QueryArgs", params={"value": value, "exc": e})


class Parametrizer(NaturalKeyModel, models.Model):
    code = models.SlugField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(
        max_length=255,
        null=True,
        blank=True,
    )
    value = models.JSONField(default=dict, blank=False, validators=[validate_queryargs])
    system = models.BooleanField(blank=True, default=False, editable=False)

    class Meta:
        verbose_name_plural = "Arguments"
        verbose_name = "Arguments"

    def clean(self) -> None:
        validate_queryargs(self.value)

    def get_matrix(self) -> List[Dict]:
        product = list(itertools.product(*self.value.values()))
        return [dict(zip(self.value.keys(), e)) for e in product]

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[Any] = None,
        update_fields: Optional[Any] = None,
    ) -> None:
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def refresh(self) -> None:
        if self.code in SYSTEM_PARAMETRIZER:
            getter: Callable = SYSTEM_PARAMETRIZER[self.code]["value"]
            self.value = getter()
            self.save()

    def __str__(self) -> str:
        return self.name


class Query(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="power_queries")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    code = models.TextField(default="qs=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True, encoder=PQJSONEncoder)
    parametrizer = models.ForeignKey(Parametrizer, on_delete=models.CASCADE, blank=True, null=True)
    sentry_error_id = models.CharField(max_length=400, blank=True, null=True)
    error_message = models.CharField(max_length=400, blank=True, null=True)

    last_run = models.DateTimeField(null=True, blank=True)

    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name or ""

    class Meta:
        verbose_name_plural = "Power Queries"
        ordering = ("name",)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[Any] = None,
        update_fields: Optional[Any] = None,
    ) -> None:
        if not self.code:
            self.code = "qs=conn.all().order_by('id')"
        super().save(force_insert, force_update, using, update_fields)

    def _invoke(self, query_id: UUID, arguments: List) -> Dict:
        query = Query.objects.get(id=query_id)
        result = query.run(persist=False, arguments=arguments)
        return result

    def update_results(self, results: Any) -> None:
        self.info["last_run_results"] = results
        self.error_message = results.get("error_message", "")
        self.sentry_error_id = results.get("sentry_error_id", "")
        self.last_run = timezone.now()
        self.save()

    def execute_matrix(self, persist: bool = True, **kwargs: Any) -> Union[Dict[str, int], Dict[str, str]]:
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
            if not args:
                raise ValueError("No valid arguments provided")
        else:
            args = [{}]
        self.error_message = None
        self.sentry_error_id = None
        self.last_run = None
        self.info = {}

        results: Dict[str, str] = {"timestamp": strftime(timezone.now(), "%Y-%m-%d %H:%M")}
        with configure_scope() as scope:
            scope.set_tag("power_query", True)
            scope.set_tag("power_query.name", self.name)
            with transaction.atomic():
                transaction.on_commit(lambda: self.update_results(results))
                for a in args:
                    try:
                        dataset, __ = self.run(persist, a)
                        if isinstance(dataset, Dataset):
                            results[str(a)] = dataset.pk
                        else:
                            results[str(a)] = str(len(dataset))

                    except QueryRunError as e:
                        logger.exception(e)
                        err = capture_exception(e)
                        results["sentry_error_id"] = str(err)
                        results["error_message"] = str(e)
                self.datasets.exclude(pk__in=[dpk for dpk in results.values() if isinstance(dpk, int)]).delete()
        return results

    def run(self, persist: bool = False, arguments: Optional[Dict] = None) -> Tuple[Union["Dataset", List], Dict]:
        model = self.target.model_class()
        connections = {
            f"{model._meta.object_name}Manager": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS)
            for model in [BusinessArea, User]
        }
        if self.owner.is_superuser:
            connections["QueryManager"] = Query.objects.filter()
        else:
            connections["QueryManager"] = Query.objects.filter(owner=self.owner)

        try:
            locals_ = {
                "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                "query": self,
                "args": arguments,
                "arguments": arguments,
                "invoke": self._invoke,
                **connections,
            }
            exec(self.code, globals(), locals_)
            result = locals_.get("result", None)
            extra = locals_.get("extra", None)

            if persist:
                info = {
                    "type": type(result).__name__,
                    "arguments": arguments,
                }
                dataset, __ = Dataset.objects.update_or_create(
                    query=self,
                    hash=dict_hash({"query": self.pk, **(arguments if arguments else {})}),
                    defaults={
                        "info": info,
                        "last_run": timezone.now(),
                        "value": pickle.dumps(result),
                        "extra": pickle.dumps(extra),
                    },
                )
                return_value = dataset, extra
            else:
                return_value = result, extra
        except Exception as e:
            raise QueryRunError(e) from e
        return return_value


class Dataset(NaturalKeyModel, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")
    value = models.BinaryField(null=True, blank=True)
    info = JSONField(default=dict, blank=True)
    extra = models.BinaryField(null=True, blank=True, help_text="Any other attribute to pass to the formatter")

    def __str__(self) -> str:
        return f"Result of {self.query.name} {self.arguments}"

    @property
    def data(self) -> Any:
        return pickle.loads(self.value)

    @property
    def size(self) -> int:
        return len(self.value)

    @property
    def arguments(self) -> Dict:
        return self.info.get("arguments", {})


class Formatter(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    content_type = models.CharField(max_length=5, choices=MIMETYPES)  # type: ignore # internal mypy error
    code = models.TextField(blank=True, null=True)

    def __str__(self) -> str:  # TODO: name is a nullable charfield?
        return self.name or ""

    def render(self, context: Dict) -> str:
        if self.content_type == "xls":
            dt = to_dataset(context["dataset"].data)
            return dt.export("xls")

        if self.code:
            tpl = Template(self.code)
        elif self.content_type == "json":
            dt = to_dataset(context["dataset"].data)
            return dt.export("json")
        elif self.content_type == "yaml":
            dt = to_dataset(context["dataset"].data)
            return dt.export("yaml")
        else:
            raise ValueError("Unable to render")

        return tpl.render(Context(context))


class Report(NaturalKeyModel, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    document_title = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")
    frequence = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Refresh every (e.g. 3 - 1/3 - mon - 1/3,Mon)",
        default="mon,tue,wed,thu,fri,sat,sun",
        validators=[FrequencyValidator()],
    )
    last_run = models.DateTimeField(null=True, blank=True)
    validity_days = models.IntegerField(default=365)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[Any] = None,
        update_fields: Optional[Any] = None,
    ) -> None:
        if not self.document_title:
            self.document_title = self.name
        super().save(force_insert, force_update, using, update_fields)

    def execute(self, run_query: bool = False) -> List:
        # TODO: refactor that
        query: Query = self.query
        result: List = []
        if run_query:
            query.execute_matrix()
        for dataset in query.datasets.all():
            if not dataset.size:
                continue
            try:
                context = dataset.arguments
                if dataset.extra:
                    context.update(pickle.loads(dataset.extra) or {})

                title = (self.document_title % context) if self.document_title else self.document_title
                output = self.formatter.render({"dataset": dataset, "report": self, "title": title, "context": context})
                res, __ = ReportDocument.objects.update_or_create(
                    report=self,
                    dataset=dataset,
                    defaults={
                        "title": title,
                        "content_type": self.formatter.content_type,
                        "output": pickle.dumps(output),
                        "arguments": dataset.arguments,
                    },
                )
                result.append([dataset.pk, len(res.output)])
            except Exception as e:
                logger.exception(e)
                result.append([dataset.pk, e])
            self.last_run = timezone.now()
        if not result:
            result = ["No Dataset available"]
        return result

    def __str__(self) -> str:
        return self.name or ""

    def get_absolute_url(self) -> str:
        return reverse("power_query:report", args=[self.pk])


class ReportDocumentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("report")


class ReportDocument(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
    arguments = models.JSONField(default=dict)
    limit_access_to = models.ManyToManyField(User, blank=True, related_name="+")
    content_type = models.CharField(max_length=5, choices=MIMETYPES)  # type: ignore # internal mypy error

    objects = ReportDocumentManager()

    class Meta:
        unique_together = ("report", "dataset")

    def __str__(self) -> str:
        return self.title

    @cached_property
    def data(self) -> Any:
        return pickle.loads(self.output)

    @cached_property
    def size(self) -> int:
        return len(self.output)

    def get_absolute_url(self) -> str:
        return reverse("power_query:document", args=[self.report.pk, self.pk])
