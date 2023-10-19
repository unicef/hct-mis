# Create your models here.
import hashlib
import logging
import sys
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Iterable, T, List, Sequence

from concurrency.fields import IntegerVersionField
from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from model_utils.managers import SoftDeletableManager
from model_utils.models import UUIDModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from decimal import Decimal

from hct_mis_api.apps.core.utils import SoftDeletableIsOriginalManager, nested_getattr

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class TimeStampedUUIDModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class SoftDeletableModelWithDate(models.Model):
    """
    An abstract base class model with a ``is_removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    Default manager returns only not-removed entries.
    """

    is_removed = models.BooleanField(default=False, db_index=True)
    removed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    objects = SoftDeletableIsOriginalManager()  # SoftDeletableManager update after data migrations last step
    all_objects = models.Manager()
    original_and_repr_objects = SoftDeletableManager(_emit_deprecation_warnings=True)

    def delete(
            self, using: Any = None, keep_parents: bool = False, soft: bool = True, *args: Any, **kwargs: Any
    ) -> Tuple[int, Dict[str, int]]:
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
            return 1, {self._meta.label: 1}

        return super().delete(using=using, *args, **kwargs)


class SoftDeletionTreeManager(TreeManager):
    def get_queryset(self, *args: Any, **kwargs: Any) -> "QuerySet":
        """
        Return queryset limited to not removed entries.
        """
        return (
            super(TreeManager, self)
            .get_queryset(*args, **kwargs)
            .filter(is_removed=False)
            .order_by(self.tree_id_attr, self.left_attr)
        )


class SoftDeletionTreeModel(TimeStampedUUIDModel, MPTTModel):
    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    objects = SoftDeletionTreeManager()
    all_objects = models.Manager()

    def delete(
            self, using: Optional[Any] = None, soft: bool = True, *args: Any, **kwargs: Any
    ) -> Optional[Tuple[int, dict[str, int]]]:
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.removed_date = timezone.now()
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)
        return None


class AbstractSession(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    SOURCE_MIS = "MIS"
    SOURCE_CA = "CA"
    # HOPE statueses
    STATUS_PROCESSING = "PROCESSING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
    # CA statuses
    STATUS_NEW = "NEW"
    STATUS_READY = "READY"
    STATUS_EMPTY = "EMPTY"
    STATUS_LOADING = "LOADING"
    STATUS_ERRORED = "ERRORED"
    STATUS_IGNORED = "IGNORED"

    source = models.CharField(
        max_length=3,
        choices=((SOURCE_MIS, "HCT-MIS"), (SOURCE_CA, "Cash Assist")),
    )
    status = models.CharField(
        max_length=11,
        choices=(
            (STATUS_NEW, "New"),
            (STATUS_READY, "Ready"),
            (STATUS_PROCESSING, "Processing"),
            (STATUS_COMPLETED, "Completed"),
            (STATUS_FAILED, "Failed"),
            (STATUS_EMPTY, "Empty"),
            (STATUS_IGNORED, "Ignored"),
            (STATUS_LOADING, "Loading"),
            (STATUS_ERRORED, "Errored"),
        ),
    )
    last_modified_date = models.DateTimeField(auto_now=True)

    business_area = models.CharField(
        max_length=20,
        help_text="""Same as the business area set on program, but
            this is set as the same value, and all other
            models this way can get easy access to the business area
            via the session.""",
    )

    sentry_id = models.CharField(max_length=100, default="", blank=True, null=True)
    traceback = models.TextField(default="", blank=True, null=True)

    class Meta:
        abstract = True

    def process_exception(self, exc: BaseException, request: Optional[HttpRequest] = None) -> Optional[int]:
        try:
            from sentry_sdk import capture_exception

            err = capture_exception(exc)
            self.sentry_id = err
        except Exception:
            pass

        try:
            from django.views.debug import ExceptionReporter

            reporter = ExceptionReporter(request, *sys.exc_info())
            self.traceback = reporter.get_traceback_html()
        except Exception as e:
            logger.exception(e)
            self.traceback = "N/A"
        finally:
            self.status = self.STATUS_FAILED

        return self.sentry_id

    def __str__(self) -> str:
        return f"#{self.id} on {self.timestamp}"


class AbstractSyncable(models.Model):
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeletableDefaultManagerModel(models.Model):
    """
    An abstract base class model with a ``is_removed`` field that
    marks entries that are not going to be used anymore, but are
    kept in db for any reason.
    Default manager returns only not-removed entries.
    """

    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    active_objects = SoftDeletableManager()
    objects = models.Manager()

    def delete(
            self, using: Any = None, keep_parents: bool = False, soft: bool = True, *args: Any, **kwargs: Any
    ) -> Tuple[int, dict[str, int]]:
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.save(using=using)
            return 1, {self._meta.label: 1}

        return super().delete(using=using, *args, **kwargs)


class ConcurrencyModel(models.Model):
    version = IntegerVersionField()

    class Meta:
        abstract = True


class UnicefIdentifiedModel(models.Model):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        super().save(*args, **kwargs)
        if self._state.adding or self.unicef_id is None:
            # due to existence of "CREATE TRIGGER" in migrations
            self.refresh_from_db(fields=["unicef_id"])


class SignatureManager(models.Manager):
    def bulk_create_with_signature(self, objs: Iterable[T], *args, **kwargs) -> List[T]:
        for obj in objs:
            obj.update_signature_hash()
        return super().bulk_create(objs, *args, **kwargs)

    def bulk_update_with_signature(self, objs: Iterable[T], fields: Sequence[str], *args, **kwargs) -> int:
        for obj in objs:
            if any(field in fields for field in obj.signature_fields):
                obj.update_signature_hash()
        new_fields = set(fields)
        if "signature_hash" not in fields:
            new_fields.add("signature_hash")
        return super().bulk_update(objs, new_fields, *args, **kwargs)


class SignatureMixin(models.Model):
    signature_hash = models.CharField(max_length=40, blank=True, editable=False)
    signature_manager = SignatureManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.update_signature_hash()
        super().save(*args, **kwargs)

    def _normalize(self, name: str, value: Any) -> Any:
        if '.' in name:
            return value
        field = self.__class__._meta.get_field(name)
        if isinstance(field, models.DecimalField) and value is not None:
            return f"{{:.{field.decimal_places}f}}".format(value)
        return value

    def update_signature_hash(self) -> None:
        if hasattr(self, "signature_fields") and isinstance(self.signature_fields, (list, tuple)):
            sha1 = hashlib.sha1()
            salt = settings.SECRET_KEY
            sha1.update(salt.encode("utf-8"))

            for field_name in self.signature_fields:
                value = nested_getattr(self, field_name, None)
                value = self._normalize(field_name, value)
                sha1.update(str(value).encode("utf-8"))
            self.signature_hash = sha1.hexdigest()
        else:
            raise ValueError("Define 'signature_fields' in class for SignatureMixin")
