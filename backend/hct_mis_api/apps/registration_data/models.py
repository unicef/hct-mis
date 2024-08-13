import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models, transaction
from django.db.models import ExpressionWrapper, Q
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.mis_datahub.models import Program
from hct_mis_api.apps.payment.api.dataclasses import SimilarityPair
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    TimeStampedUUIDModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)

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


class RegistrationDataImport(TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "import_date",
            "imported_by",
            "data_source",
            "number_of_individuals",
            "number_of_households",
            "datahub_id",
            "error_message",
        ]
    )
    LOADING = "LOADING"
    IMPORT_SCHEDULED = "IMPORT_SCHEDULED"
    IMPORTING = "IMPORTING"
    IN_REVIEW = "IN_REVIEW"
    MERGE_SCHEDULED = "MERGE_SCHEDULED"
    MERGING = "MERGING"
    MERGED = "MERGED"
    DEDUPLICATION_FAILED = "DEDUPLICATION_FAILED"
    DEDUPLICATION = "DEDUPLICATION"
    REFUSED_IMPORT = "REFUSED"
    IMPORT_ERROR = "IMPORT_ERROR"
    MERGE_ERROR = "MERGE_ERROR"
    STATUS_CHOICE = (
        (LOADING, _("Loading")),
        (DEDUPLICATION, _("Deduplication")),
        (DEDUPLICATION_FAILED, _("Deduplication Failed")),
        (IMPORT_SCHEDULED, _("Import Scheduled")),
        (IMPORTING, _("Importing")),
        (IMPORT_ERROR, _("Import Error")),
        (IN_REVIEW, _("In Review")),
        (MERGE_SCHEDULED, _("Merge Scheduled")),
        (MERGED, _("Merged")),
        (MERGING, _("Merging")),
        (MERGE_ERROR, _("Merge Error")),
        (REFUSED_IMPORT, _("Refused import")),
    )
    XLS = "XLS"
    KOBO = "KOBO"
    API = "API"
    FLEX_REGISTRATION = "FLEX_REGISTRATION"
    EDOPOMOGA = "EDOPOMOGA"
    PROGRAM_POPULATION = "PROGRAM_POPULATION"
    DATA_SOURCE_CHOICE = (
        (XLS, "Excel"),
        (KOBO, "KoBo"),
        (FLEX_REGISTRATION, "Flex Registration"),
        (API, "Flex API"),
        (EDOPOMOGA, "eDopomoga"),
        (PROGRAM_POPULATION, "Program Population"),
    )

    DEDUP_ENGINE_PENDING = "PENDING"
    DEDUP_ENGINE_UPLOADED = "UPLOADED"
    DEDUP_ENGINE_IN_PROGRESS = "IN_PROGRESS"
    DEDUP_ENGINE_FINISHED = "FINISHED"
    DEDUP_ENGINE_ERROR = "ERROR"

    DEDUP_ENGINE_STATUS_CHOICE = (
        (DEDUP_ENGINE_PENDING, _("Pending")),
        (DEDUP_ENGINE_UPLOADED, _("Uploaded")),
        (DEDUP_ENGINE_IN_PROGRESS, _("In Progress")),
        (DEDUP_ENGINE_FINISHED, _("Finished")),
        (DEDUP_ENGINE_ERROR, _("Error")),
    )
    name = CICharField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default=IN_REVIEW, db_index=True)
    import_date = models.DateTimeField(auto_now_add=True, db_index=True)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="registration_data_imports",
        on_delete=models.CASCADE,
        null=True,
    )
    data_source = models.CharField(
        max_length=255,
        choices=DATA_SOURCE_CHOICE,
    )
    number_of_individuals = models.PositiveIntegerField(db_index=True)
    number_of_households = models.PositiveIntegerField(db_index=True)

    batch_duplicates = models.PositiveIntegerField(default=0)
    batch_possible_duplicates = models.PositiveIntegerField(default=0)
    batch_unique = models.PositiveIntegerField(default=0)
    golden_record_duplicates = models.PositiveIntegerField(default=0)
    golden_record_possible_duplicates = models.PositiveIntegerField(default=0)
    golden_record_unique = models.PositiveIntegerField(default=0)

    datahub_id = models.UUIDField(null=True, default=None, db_index=True, blank=True)
    error_message = models.TextField(blank=True)
    sentry_id = models.CharField(max_length=100, default="", blank=True, null=True)

    pull_pictures = models.BooleanField(default=True)
    business_area = models.ForeignKey(BusinessArea, null=True, on_delete=models.CASCADE)
    screen_beneficiary = models.BooleanField(default=False)
    excluded = models.BooleanField(default=False, help_text="Exclude RDI in UI")
    # TODO: in future will use one program per RDI after migration
    program = models.ForeignKey(
        "program.Program",
        null=True,
        blank=True,
        db_index=True,
        related_name="registration_imports",
        on_delete=models.SET_NULL,
    )
    erased = models.BooleanField(default=False, help_text="Abort RDI")
    refuse_reason = models.CharField(max_length=100, blank=True, null=True)
    allow_delivery_mechanisms_validation_errors = models.BooleanField(default=False)
    import_data = models.OneToOneField(
        "ImportData",
        related_name="registration_data_import_hope",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    deduplication_engine_status = models.CharField(
        max_length=255, choices=DEDUP_ENGINE_STATUS_CHOICE, null=True, default=None
    )  # TODO on RDI create set to PENDING if program flag enabled
    # if program flag enabled in admin set all RDI to PENDING

    def __str__(self) -> str:
        return self.name

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Registration data import"

    def should_check_against_sanction_list(self) -> bool:
        return self.screen_beneficiary

    @classmethod
    def get_choices(
        cls, business_area_slug: Optional[str] = None, program_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = Q(status=cls.MERGED)
        if business_area_slug:
            query &= Q(business_area__slug=business_area_slug)
        if program_id:
            query &= Q(program_id=program_id)
        queryset = cls.objects.filter(query)
        return [
            {
                "label": {"English(EN)": f"{rdi.name}"},
                "value": rdi.id,
            }
            for rdi in queryset
        ]

    def can_be_merged(self) -> bool:
        return self.status in (self.IN_REVIEW, self.MERGE_ERROR)


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
    STATUS_DELIVERY_MECHANISMS_VALIDATION_ERROR = "DELIVERY_MECHANISMS_VALIDATION_ERROR"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_RUNNING, _("Running")),
        (STATUS_FINISHED, _("Finished")),
        (STATUS_ERROR, _("Error")),
        (STATUS_VALIDATION_ERROR, _("Validation Error")),
        (STATUS_DELIVERY_MECHANISMS_VALIDATION_ERROR, _("Delivery Mechanisms Validation Error")),
    )
    status = models.CharField(max_length=40, default=STATUS_FINISHED, choices=STATUS_CHOICES)
    business_area_slug = models.CharField(max_length=200, blank=True)
    file = models.FileField(null=True)
    data_type = models.CharField(max_length=4, choices=DATA_TYPE_CHOICES, default=XLSX)
    number_of_households = models.PositiveIntegerField(null=True)
    number_of_individuals = models.PositiveIntegerField(null=True)
    error = models.TextField(blank=True)
    validation_errors = models.TextField(blank=True)
    delivery_mechanisms_validation_errors = models.TextField(blank=True)
    created_by_id = models.UUIDField(null=True)


class KoboImportData(ImportData):
    kobo_asset_id = models.CharField(max_length=100)
    only_active_submissions = models.BooleanField(default=True)
    pull_pictures = models.BooleanField(default=True)


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
        ImportData,
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
        return RegistrationDataImport.objects.get(datahub_id=self.id)


class KoboImportedSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True)
    kobo_submission_uuid = models.UUIDField()  # ImportedHousehold.kobo_submission_uuid
    kobo_asset_id = models.CharField(max_length=150)  # ImportedHousehold.detail_id
    kobo_submission_time = models.DateTimeField()  # ImportedHousehold.kobo_submission_time
    imported_household = models.ForeignKey("household.Household", blank=True, null=True, on_delete=models.SET_NULL)
    amended = models.BooleanField(default=False, blank=True)

    registration_data_import = models.ForeignKey(
        RegistrationDataImport,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


class DeduplicationEngineSimilarityPairManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(
                is_duplicate=ExpressionWrapper(
                    models.Case(
                        models.When(similarity_score__gte=models.F("program__threshold"), then=models.Value(True)),
                        default=models.Value(False),
                        output_field=models.BooleanField(),
                    ),
                    output_field=models.BooleanField(),
                )
            )
        )

    def duplicates(self) -> models.QuerySet:
        return self.get_queryset().filter(is_duplicate=True)


class DeduplicationEngineSimilarityPair(models.Model):
    program = models.ForeignKey(
        "program.Program", related_name="deduplication_engine_similarity_pairs", on_delete=models.CASCADE
    )
    individual1 = models.ForeignKey(
        "household.Individual", related_name="biometric_duplicates_1", on_delete=models.CASCADE
    )
    individual2 = models.ForeignKey(
        "household.Individual", related_name="biometric_duplicates_2", on_delete=models.CASCADE
    )
    similarity_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    objects = DeduplicationEngineSimilarityPairManager()

    class Meta:
        unique_together = ("individual1", "individual2")
        constraints = [
            # Prevent an Individual from being marked as a duplicate of itself
            models.CheckConstraint(
                check=~models.Q(individual1=models.F("individual2")), name="prevent_self_duplicates"
            ),
            # Enforce a consistent ordering to avoid duplicate entries in reverse
            models.CheckConstraint(
                check=models.Q(individual1__lt=models.F("individual2")), name="individual1_lt_individual2"
            ),
        ]

    @classmethod
    def bulk_add_duplicates(cls, deduplication_set_id: str, duplicates_data: List[SimilarityPair]) -> None:
        program = Program.objects.get(deduplication_set_id=deduplication_set_id)
        duplicates = []
        for pair in duplicates_data:
            # Ensure consistent ordering of individual1 and individual2
            individual1, individual2 = sorted([pair.first, pair.second], key=lambda x: x.id)

            duplicates.append(
                cls(
                    program=program,
                    individual1_id=individual1.id,
                    individual2_id=individual2.id,
                    similarity_score=pair.similarity_score,
                )
            )

        with transaction.atomic():
            cls.objects.bulk_create(duplicates, ignore_conflicts=True)

    @property
    def _is_duplicate(self) -> bool:
        return self.similarity_score >= self.program.biometric_deduplication_threshold
