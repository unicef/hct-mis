import json
import logging
import re
from datetime import date
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.contrib.gis.db.models import PointField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    validate_image_file_extension,
)
from django.db import models
from django.db.models import JSONField
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.languages import Languages
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import (
    BLANK,
    DATA_SHARING_CHOICES,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DISABILITY_CHOICES,
    MARITAL_STATUS_CHOICE,
    NOT_DISABLED,
    NOT_PROVIDED,
    OBSERVED_DISABILITY_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    REGISTRATION_METHOD_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_ALTERNATE,
    ROLE_CHOICE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    UNIQUE,
    WORK_STATUS_CHOICE,
)
from hct_mis_api.apps.registration_datahub.utils import combine_collections
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from hct_mis_api.apps.utils.phone import (
    calculate_phone_numbers_validity,
    recalculate_phone_numbers_validity,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.registration_data.models import RegistrationDataImport

logger = logging.getLogger(__name__)

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

COLLECT_TYPE_UNKNOWN = ""
COLLECT_TYPE_NONE = "0"
COLLECT_TYPE_FULL = "1"
COLLECT_TYPE_PARTIAL = "2"

COLLECT_TYPES = (
    (COLLECT_TYPE_UNKNOWN, _("Unknown")),
    (COLLECT_TYPE_PARTIAL, _("Partial individuals collected")),
    (COLLECT_TYPE_FULL, _("Full individual collected")),
    (COLLECT_TYPE_NONE, _("No individual data")),
)


class ImportedHousehold(TimeStampedUUIDModel):
    class CollectType(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        SINGLE = "SINGLE", "Single"

    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.BooleanField(null=True)
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField()
    size = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=1024, blank=True, default=BLANK)
    country = CountryField()
    zip_code = models.CharField(max_length=12, blank=True, null=True)
    """location contains lowest administrative area info"""
    admin_area = models.CharField(max_length=255, blank=True, default=BLANK)
    admin_area_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin1 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin1_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin2_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin3 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin3_title = models.CharField(max_length=255, blank=True, default=BLANK)
    admin4 = models.CharField(max_length=255, blank=True, default=BLANK)
    admin4_title = models.CharField(max_length=255, blank=True, default=BLANK)
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
    collect_individual_data = models.CharField(max_length=250, choices=COLLECT_TYPES, default=COLLECT_TYPE_UNKNOWN)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK)
    kobo_submission_uuid = models.UUIDField(null=True, default=None)
    kobo_submission_time = models.DateTimeField(max_length=150, blank=True, null=True)
    # TODO: remove 'kobo_asset_id' and 'row_id' after migrate data
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    detail_id = models.CharField(
        max_length=150, blank=True, null=True, help_text="Kobo asset ID, Xlsx row ID, Aurora source ID"
    )
    program_registration_id = models.CharField(max_length=50, blank=True, null=True)
    enumerator_rec_id = models.PositiveIntegerField(blank=True, null=True)
    flex_registrations_record = models.ForeignKey(
        "registration_datahub.Record",
        related_name="imported_households",
        on_delete=models.SET_NULL,
        null=True,
    )
    mis_unicef_id = models.CharField(max_length=255, null=True)
    program_id = models.UUIDField(
        null=True, db_index=True, blank=True
    )  # TODO temporary null=True until we migrate backward all data
    collect_type = models.CharField(choices=CollectType.choices, default=CollectType.STANDARD.value, max_length=8)

    @property
    def business_area(self) -> str:
        return self.registration_data_import.business_area

    @cached_property
    def primary_collector(self) -> Optional[User]:
        return self.individuals_and_roles.get(role=ROLE_PRIMARY).individual

    @cached_property
    def alternate_collector(self) -> Optional[User]:
        try:
            return self.individuals_and_roles.filter(role=ROLE_ALTERNATE).first().individual
        except AttributeError:
            return None

    def set_admin_areas(self) -> None:
        admins = {
            "admin1": self.admin1,
            "admin2": self.admin2,
            "admin3": self.admin3,
            "admin4": self.admin4,
        }

        for admin_key, admin_value in admins.items():
            if admin_value:
                admin_area = Area.objects.filter(p_code=admin_value).first()
                if admin_area:
                    self.admin_area = admin_value
                    self.admin_area_title = admin_area.name
                    setattr(self, f"{admin_key}_title", admin_area.name)

    def __str__(self) -> str:
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
    phone_no_valid = models.BooleanField(null=True)
    phone_no_alternative = PhoneNumberField(blank=True, default=BLANK)
    phone_no_alternative_valid = models.BooleanField(null=True)
    email = models.CharField(max_length=255, blank=True)
    payment_delivery_phone_no = PhoneNumberField(blank=True, default=BLANK)
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
    # TODO: remove 'kobo_asset_id' and 'row_id' after migrate data
    kobo_asset_id = models.CharField(max_length=150, blank=True, default=BLANK)
    row_id = models.PositiveIntegerField(blank=True, null=True)
    detail_id = models.CharField(
        max_length=150, blank=True, null=True, help_text="Kobo asset ID, Xlsx row ID, Aurora source ID"
    )
    disability_certificate_picture = models.ImageField(blank=True, null=True)
    preferred_language = models.CharField(max_length=6, choices=Languages.get_tuple(), null=True, blank=True)
    mis_unicef_id = models.CharField(max_length=255, null=True)
    program_id = models.UUIDField(
        null=True, db_index=True, blank=True
    )  # TODO temporary null=True until we migrate backward all data
    age_at_registration = models.PositiveSmallIntegerField(null=True, blank=True)

    @property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def get_hash_key(self) -> str:
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
            "relationship",
        )
        values = [str(getattr(self, field)).lower() for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    def __str__(self) -> str:
        return self.full_name

    @property
    def business_area(self) -> BusinessArea:
        return self.registration_data_import.business_area

    @property
    def role(self) -> Optional[str]:
        role = self.households_and_roles.first()
        return role.role if role is not None else ROLE_NO_ROLE

    def validate_phone_numbers(self) -> None:
        calculate_phone_numbers_validity(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        recalculate_phone_numbers_validity(self, ImportedIndividual)
        super().save(*args, **kwargs)


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
    LOADING = "LOADING"
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    DONE = "DONE"
    IMPORT_DONE_CHOICES = (
        (LOADING, _("Loading")),
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
        permissions = (["api_upload", "Can upload"],)

    def __str__(self) -> str:
        return self.name

    @property
    def business_area(self) -> str:
        return self.business_area_slug

    @property
    def linked_rdi(self) -> "RegistrationDataImport":
        from hct_mis_api.apps.registration_data.models import RegistrationDataImport

        return RegistrationDataImport.objects.get(datahub_id=self.id)


class ImportData(TimeStampedUUIDModel):
    XLSX = "XLSX"
    JSON = "JSON"
    FLEX_REGISTRATION = "FLEX"
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
    label = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    is_identity_document = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.label}"


class ImportedDocument(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("ImportedIndividual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey(
        "ImportedDocumentType",
        related_name="documents",
        on_delete=models.CASCADE,
    )
    country = CountryField(default="U")
    doc_date = models.DateField(blank=True, null=True, default=None)
    issuance_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")


class ImportedIndividualIdentity(models.Model):
    individual = models.ForeignKey(
        "ImportedIndividual",
        related_name="identities",
        on_delete=models.CASCADE,
    )
    document_number = models.CharField(
        max_length=255,
    )
    country = CountryField(default="U")
    partner = models.CharField(max_length=100, null=True)

    class Meta:
        verbose_name_plural = "Imported Individual Identities"

    def __str__(self) -> str:
        return f"{self.partner} {self.individual} {self.document_number}"


class KoboImportedSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    kobo_submission_uuid = models.UUIDField()  # ImportedHousehold.kobo_submission_uuid
    kobo_asset_id = models.CharField(max_length=150)  # ImportedHousehold.detail_id
    kobo_submission_time = models.DateTimeField()  # ImportedHousehold.kobo_submission_time
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
    STATUS_TO_IMPORT = "TO_IMPORT"
    STATUS_IMPORTED = "IMPORTED"
    STATUS_ERROR = "ERROR"
    STATUSES_CHOICES = (
        (STATUS_TO_IMPORT, "To import"),
        (STATUS_IMPORTED, "Imported"),
        (STATUS_ERROR, "Error"),
    )

    registration = models.IntegerField(db_index=True)
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
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUSES_CHOICES, null=True, blank=True)

    unique_field = models.CharField(blank=True, null=True, max_length=255, db_index=True)
    size = models.IntegerField(blank=True, null=True)
    counters = models.JSONField(blank=True, null=True)

    fields = models.JSONField(null=True, blank=True)
    files = models.BinaryField(null=True, blank=True)

    index1 = models.CharField(null=True, blank=True, max_length=255, db_index=True)
    index2 = models.CharField(null=True, blank=True, max_length=255, db_index=True)
    index3 = models.CharField(null=True, blank=True, max_length=255, db_index=True)

    def mark_as_invalid(self, msg: str) -> None:
        self.error_message = msg
        self.status = self.STATUS_ERROR
        self.save()

    def mark_as_imported(self) -> None:
        self.status = self.STATUS_IMPORTED
        self.save()

    def get_data(self) -> Dict:
        if self.storage:
            return json.loads(self.storage.tobytes().decode())
        if not self.files:
            return self.fields
        files = json.loads(self.files.tobytes().decode())
        return combine_collections(files, self.fields)


class ImportedBankAccountInfo(TimeStampedUUIDModel):
    individual = models.ForeignKey(
        "registration_datahub.ImportedIndividual", related_name="bank_account_info", on_delete=models.CASCADE
    )
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=64)
    debit_card_number = models.CharField(max_length=255, blank=True, default="")
    bank_branch_name = models.CharField(max_length=255, blank=True, default="")
    account_holder_name = models.CharField(max_length=255, blank=True, default="")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.bank_account_number:
            self.bank_account_number = str(self.bank_account_number).replace(" ", "")
        if self.debit_card_number:
            self.debit_card_number = str(self.debit_card_number).replace(" ", "")
        super().save(*args, **kwargs)
