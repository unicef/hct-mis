# Create your models here.
from django.db import models
from model_utils.models import UUIDModel
from mptt.managers import TreeManager
from mptt.models import MPTTModel


class TimeStampedUUIDModel(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeletionTreeManager(TreeManager):
    def get_queryset(self, *args, **kwargs):
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

    def delete(self, using=None, soft=True, *args, **kwargs):
        """
        Soft delete object (set its ``is_removed`` field to True).
        Actually delete object if setting ``soft`` to False.
        """
        if soft:
            self.is_removed = True
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


class AbstractSession(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=3, choices=(("MIS", "HCT-MIS"), ("CA", "Cash Assist")),
    )
    status = models.CharField(
        max_length=11,
        choices=(
            ("NEW", "New"),
            ("READY", "Ready"),
            ("PROCESSING", "Processing"),
            ("COMPLETED", "Completed"),
            ("FAILED", "Failed"),
        ),
    )
    last_modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SessionModel(models.Model):
    session_id = models.ForeignKey(
        "cash_assist_datahub.Session", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
