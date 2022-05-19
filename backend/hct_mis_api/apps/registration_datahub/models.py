import json
import logging
import re
from datetime import date
from typing import List

from django.contrib.gis.db.models import PointField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    validate_image_file_extension,
)
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.household.models import (
    BLANK,
    DATA_SHARING_CHOICES,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DISABILITY_CHOICES,
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    NOT_DISABLED,
    NOT_PROVIDED,
    OBSERVED_DISABILITY_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    REGISTRATION_METHOD_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    UNIQUE,
    WORK_STATUS_CHOICE,
    YES_NO_CHOICE,
)
from hct_mis_api.apps.registration_datahub.templatetags.smart_register import is_image
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel

SIMILAR_IN_BATCH = "SIMILAR_IN_BATCH"
DUPLICATE_IN_BATCH = "DUPLICATE_IN_BATCH"
UNIQUE_IN_BATCH = "UNIQUE_IN_BATCH"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_BATCH_STATUS_CHOICE = (
    (SIMILAR_IN_BATCH, "Similar in batch"),
    (DUPLICATE_IN_BATCH, "Duplicate in batch"),
    (UNIQUE_IN_BATCH, "Unique in batch"),
    (NOT_PROCESSED, "Not Processed"),
)

logger = logging.getLogger(__name__)


class ImportedHousehold(TimeStampedUUIDModel):
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(null=True)
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField()
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True, default=BLANK)
    country = CountryField()
    admin1 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin1_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2_title = models.CharField(max_length=255, blank=True, default=BLANK)
    geopoint = PointField(null=True, default=None)
    female_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    pregnant_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    head_of_household = models.OneToOneField("ImportedIndividual", on_delete=models.CASCADE, null=True)
    fchild_hoh = models.BooleanField(null=True)
    child_hoh = models.BooleanField(null=True)
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="households",
        on_delete=models.CASCADE,
    )
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    returnee = models.BooleanField(null=True)
    flex_fields = JSONField(default=dict)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True)
    name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES, blank=True, default=BLANK)
    org_name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    village = models.CharField(max_length=250, blank=True, default=BLANK)
    registration_method = models.CharField(max_length=250, choices=REGISTRATION_METHOD_CHOICES, default=BLANK)
    collect_individual_data = models.CharField(max_length=250, choices=YES_NO_CHOICE, default=BLANK)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK)
    kobo_submission_uuid = models.UUIDField(null=True, default=None)
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    kobo_submission_time = models.DateTimeField(max_length=150, blank=True, null=True)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    diia_rec_id = models.CharField(max_length=50, blank=True, default=BLANK)
    flex_registrations_record = models.ForeignKey(
        "registration_datahub.Record",
        related_name="imported_households",
        on_delete=models.SET_NULL,
        null=True,
    )
    mis_unicef_id = models.CharField(max_length=255, null=True)

    @property
    def business_area(self):
        return self.registration_data_import.business_area

    def __str__(self):
        return f"Household ID: {self.id}"


class ImportedIndividual(TimeStampedUUIDModel):
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    given_name = models.CharField(max_length=85, blank=True, default=BLANK)
    middle_name = models.CharField(max_length=85, blank=True, default=BLANK)
    family_name = models.CharField(max_length=85, blank=True, default=BLANK)
    relationship = models.CharField(
        max_length=255,
        blank=True,
        choices=RELATIONSHIP_CHOICE,
        default=BLANK,
    )
    sex = models.CharField(
        max_length=255,
        choices=SEX_CHOICE,
    )
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(
        max_length=255,
        choices=MARITAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True, default=BLANK)
    phone_no_alternative = PhoneNumberField(blank=True, default=BLANK)
    household = models.ForeignKey(
        "ImportedHousehold",
        null=True,
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default=NOT_DISABLED)
    work_status = models.CharField(
        max_length=20,
        choices=WORK_STATUS_CHOICE,
        blank=True,
        default=NOT_PROVIDED,
    )
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
        blank=True,
    )
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
        blank=True,
    )
    deduplication_batch_results = JSONField(default=dict)
    deduplication_golden_record_results = JSONField(default=dict)
    flex_fields = JSONField(default=dict)
    pregnant = models.BooleanField(null=True)
    observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE)
    seeing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    hearing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    physical_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    memory_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    selfcare_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    comms_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    who_answers_phone = models.CharField(max_length=150, blank=True)
    who_answers_alt_phone = models.CharField(max_length=150, blank=True)
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    disability_certificate_picture = models.ImageField(blank=True, null=True)
    mis_unicef_id = models.CharField(max_length=255, null=True)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def get_hash_key(self):
        from hashlib import sha256

        fields = (
            "given_name",
            "middle_name",
            "family_name",
            "full_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)).lower() for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    def __str__(self):
        return self.full_name

    @property
    def business_area(self):
        return self.registration_data_import.business_area


class ImportedIndividualRoleInHousehold(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "ImportedIndividual",
        on_delete=models.CASCADE,
        related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "ImportedHousehold",
        on_delete=models.CASCADE,
        related_name="individuals_and_roles",
    )
    role = models.CharField(
        max_length=255,
        blank=True,
        choices=ROLE_CHOICE,
    )

    class Meta:
        unique_together = ("role", "household")


class RegistrationDataImportDatahub(TimeStampedUUIDModel):
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    DONE = "DONE"
    IMPORT_DONE_CHOICES = (
        (NOT_STARTED, _("Not Started")),
        (STARTED, _("Started")),
        (DONE, _("Done")),
    )

    name = models.CharField(max_length=255, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    hct_id = models.UUIDField(null=True, db_index=True)
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import",
        on_delete=models.CASCADE,
        null=True,
    )
    import_done = models.CharField(max_length=15, choices=IMPORT_DONE_CHOICES, default=NOT_STARTED)
    business_area_slug = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def business_area(self):
        return self.business_area_slug


class ImportData(TimeStampedUUIDModel):
    XLSX = "XLSX"
    JSON = "JSON"
    FLEX_REGISTRATION = "FLEX"
    # TODO: add Diia
    DATA_TYPE_CHOICES = (
        (XLSX, _("XLSX File")),
        (JSON, _("JSON File")),
        (FLEX_REGISTRATION, _("Flex Registration")),
    )
    STATUS_PENDING = "PENDING"
    STATUS_RUNNING = "RUNNING"
    STATUS_FINISHED = "FINISHED"
    STATUS_ERROR = "ERROR"
    STATUS_VALIDATION_ERROR = "VALIDATION_ERROR"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_RUNNING, _("Running")),
        (STATUS_FINISHED, _("Finished")),
        (STATUS_ERROR, _("Error")),
        (STATUS_VALIDATION_ERROR, _("Validation Error")),
    )
    status = models.CharField(max_length=20, default=STATUS_FINISHED, choices=STATUS_CHOICES)
    business_area_slug = models.CharField(max_length=200, blank=True)
    file = models.FileField(null=True)
    data_type = models.CharField(max_length=4, choices=DATA_TYPE_CHOICES, default=XLSX)
    number_of_households = models.PositiveIntegerField(null=True)
    number_of_individuals = models.PositiveIntegerField(null=True)
    error = models.TextField(blank=True)
    validation_errors = models.TextField(blank=True)
    created_by_id = models.UUIDField(null=True)


class KoboImportData(ImportData):
    kobo_asset_id = models.CharField(max_length=100)
    only_active_submissions = models.BooleanField(default=True)


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey(
        "ImportedDocumentType",
        related_name="validators",
        on_delete=models.CASCADE,
    )
    regex = models.CharField(max_length=100, default=".*")


class ImportedDocumentType(TimeStampedUUIDModel):
    country = CountryField(default="U")
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label} in {self.country}"


class ImportedDocument(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("ImportedIndividual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey(
        "ImportedDocumentType",
        related_name="documents",
        on_delete=models.CASCADE,
    )
    doc_date=models.DateField(blank=True, null=True, default=None)

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")


class ImportedAgency(models.Model):
    type = models.CharField(
        max_length=100,
    )
    label = models.CharField(
        max_length=100,
    )
    country = CountryField()

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label}"


class ImportedIndividualIdentity(models.Model):
    agency = models.ForeignKey("ImportedAgency", related_name="identities", on_delete=models.CASCADE)
    individual = models.ForeignKey(
        "ImportedIndividual",
        related_name="identities",
        on_delete=models.CASCADE,
    )
    document_number = models.CharField(
        max_length=255,
    )

    class Meta:
        verbose_name_plural = 'Imported Individual Identities'

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"


class KoboImportedSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    kobo_submission_uuid = models.UUIDField()
    kobo_asset_id = models.CharField(max_length=150)
    kobo_submission_time = models.DateTimeField()
    # we use on_delete=models.SET_NULL because we want to be able to delete
    # ImportedHousehold without loosing track of importing
    imported_household = models.ForeignKey(ImportedHousehold, blank=True, null=True, on_delete=models.SET_NULL)
    amended = models.BooleanField(default=False, blank=True)

    registration_data_import = models.ForeignKey(
        RegistrationDataImportDatahub,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


class Record(models.Model):
    registration = models.IntegerField()
    timestamp = models.DateTimeField(db_index=True)
    storage = models.BinaryField(null=True, blank=True)
    registration_data_import = models.ForeignKey(
        "registration_datahub.RegistrationDataImportDatahub",
        related_name="records",
        on_delete=models.SET_NULL,
        null=True,
    )
    ignored = models.BooleanField(default=False, blank=True, null=True, db_index=True)
    source_id = models.IntegerField(db_index=True)
    data = models.JSONField(default=dict, blank=True, null=True)

    @classmethod
    def extract(cls, records_ids: List[int], raise_exception=False):
        def _filter(d):
            if isinstance(d, list):
                return [_filter(v) for v in d]
            elif isinstance(d, dict):
                return {k: _filter(v) for k, v in d.items()}
            elif is_image(d):
                return "::image::"
            else:
                return d

        for record_id in records_ids:
            record = cls.objects.get(pk=record_id)
            try:
                extracted = json.loads(record.storage.tobytes().decode())
                record.data = _filter(extracted)

                individuals = record.data.get("individuals", {})
                collectors = [individual for individual in individuals if individual.get("role_i_c", "n") == "y"]
                heads = [individual for individual in individuals if individual.get("relationship_i_c") == "head"]

                record.data["w_counters"] = {
                    "individuals_num": len(individuals),
                    "collectors_num": len(collectors),
                    "head": len(heads),
                    "valid_phones": len([individual for individual in individuals if individual.get("phone_no_i_c")]),
                    "valid_taxid": len(
                        [head for head in heads if head.get("tax_id_no_i_c") and head.get("bank_account")]
                    ),
                    "valid_payment": len(
                        [
                            individual
                            for individual in individuals
                            if individual.get("tax_id_no_i_c") and individual.get("bank_account")
                        ]
                    ),
                    "birth_certificate": len(
                        [
                            individual
                            for individual in individuals
                            if individual.get("birth_certificate_picture") == "::image::"
                        ]
                    ),
                    "disability_certificate_match": (
                        len(
                            [
                                individual
                                for individual in individuals
                                if individual.get("disability_certificate_picture") == "::image::"
                            ]
                        )
                        == len([individual for individual in individuals if individual.get("disability_i_c") == "y"])
                    ),
                    "collector_bank_account": len([individual.get("bank_account") for individual in collectors]) > 0,
                }
                record.save()
            except Exception as e:
                if raise_exception:
                    raise
                logger.exception(e)


class ImportedBankAccountInfo(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "registration_datahub.ImportedIndividual", related_name="bank_account_info", on_delete=models.CASCADE
    )
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=64)
    debit_card_number = models.CharField(max_length=255, blank=True, default="")


class DiiaHousehold(TimeStampedUUIDModel):
    rec_id = models.CharField(max_length=20, blank=True, default=BLANK)
    vpo_doc = ImageField(validators=[validate_image_file_extension], blank=True)
    vpo_doc_id = models.CharField(max_length=128, blank=True, default=BLANK)
    vpo_doc_date = models.DateField(blank=True)
    address = models.CharField(max_length=255, blank=True, default=BLANK)
    consent = models.BooleanField()
    head_of_household = models.OneToOneField("DiiaIndividual", on_delete=models.CASCADE, null=True)

    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="diia_households",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    imported_household = models.ForeignKey(
        "ImportedHousehold",
        on_delete=models.CASCADE,
        related_name="diia_households",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Diia Household ID: {self.id}"

    @property
    def head_of_household_full_name(self):
        return self.head_of_household.full_name if self.head_of_household else "-"


class DiiaIndividual(TimeStampedUUIDModel):
    individual_id = models.CharField(max_length=128, blank=True)  # RNOKPP
    last_name = models.CharField(max_length=85, blank=True, default=BLANK)
    first_name = models.CharField(max_length=85, blank=True, default=BLANK)
    second_name = models.CharField(max_length=85, blank=True, default=BLANK)
    relationship = models.CharField(max_length=255, blank=True, choices=RELATIONSHIP_CHOICE, default=BLANK)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE)
    birth_date = models.DateField()
    birth_doc = models.CharField(max_length=128, blank=True)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICE)
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default=NOT_DISABLED)
    iban = models.CharField(max_length=255, blank=True, default=BLANK)
    bank_name = models.CharField(max_length=255, blank=True, default=BLANK)

    household = models.ForeignKey(
        "DiiaHousehold",
        null=True,
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "RegistrationDataImportDatahub",
        related_name="diia_individuals",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    imported_individual = models.ForeignKey(
        "ImportedIndividual",
        on_delete=models.CASCADE,
        related_name="diia_individuals",
        null=True,
        blank=True
    )

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.second_name}"
