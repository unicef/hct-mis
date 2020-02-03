from django.conf import settings
from django.db import models

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Grievance(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    opened_date = models.DateTimeField()
    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="grievances",
    )
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="grievances_assigned",
        null=True,
    )

    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="grievance_created",
        null=True,
    )

    def __str__(self):
        return self.name


class Note(TimeStampedUUIDModel):
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="notes_created",
        null=True,
    )
    description = models.TextField(null=True, blank=True)
