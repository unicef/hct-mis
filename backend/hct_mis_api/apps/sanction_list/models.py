from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from django_countries.fields import CountryField

from utils.models import TimeStampedUUIDModel


class SanctionListIndividualQuerySet(models.QuerySet):
    def delete(self):
        return super().update(active=False)

    def hard_delete(self):
        return super().delete()

    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.exclude(active=False)


class ActiveIndividualsManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop("active_only", True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SanctionListIndividualQuerySet(self.model).active()
        return SanctionListIndividualQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SanctionListIndividual(TimeStampedUUIDModel):
    data_id = models.PositiveIntegerField()
    version_num = models.PositiveIntegerField()
    first_name = models.CharField(max_length=85)
    second_name = models.CharField(max_length=85, blank=True, default="")
    third_name = models.CharField(max_length=85, blank=True, default="")
    fourth_name = models.CharField(max_length=85, blank=True, default="")
    full_name = models.CharField(max_length=255)
    name_original_script = models.CharField(
        max_length=255, blank=True, default=""
    )
    un_list_type = models.CharField(max_length=100, blank=True, default="")
    reference_number = models.CharField(max_length=50, unique=True)
    listed_on = models.DateTimeField()
    comments = models.TextField(blank=True, default="")
    designation = models.TextField(blank=True, default="")
    list_type = models.CharField(max_length=50)
    alias_name = models.ForeignKey(
        "SanctionListIndividualAliasName",
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    street = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=255, blank=True, default="")
    state_province = models.CharField(max_length=255, blank=True, default="")
    address_note = models.CharField(max_length=255, blank=True, default="")
    country_of_birth = CountryField(blank=True, default="")
    active = models.BooleanField(default=True)
    history = AuditlogHistoryField(pk_indexable=False)

    objects = ActiveIndividualsManager()
    all_objects = ActiveIndividualsManager(active_only=False)


class SanctionListIndividualDocument(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255)
    type_of_document = models.CharField(max_length=255)
    date_of_issue = models.CharField(
        max_length=255, blank=True, null=True, default=""
    )
    issuing_country = CountryField(blank=True, default="")
    note = models.CharField(max_length=255, blank=True, default="")
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="documents",
    )


class SanctionListIndividualNationalities(TimeStampedUUIDModel):
    nationality = CountryField()
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="nationalities",
    )


class SanctionListIndividualCountries(TimeStampedUUIDModel):
    country = CountryField()
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="countries",
    )


class SanctionListIndividualAliasName(TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="alias_names",
    )


class SanctionListIndividualDateOfBirth(TimeStampedUUIDModel):
    date = models.DateField()
    individual = models.ForeignKey(
        "SanctionListIndividual",
        on_delete=models.CASCADE,
        related_name="dates_of_birth",
    )


class UploadedXLSXFile(TimeStampedUUIDModel):
    file = models.FileField()
    associated_email = models.EmailField()


auditlog.register(SanctionListIndividual)
