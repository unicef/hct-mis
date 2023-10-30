from decimal import Decimal
from typing import Union

from django.contrib.postgres.fields import CICharField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from model_utils.models import SoftDeletableModel

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    ConcurrencyModel,
    TimeStampedUUIDModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)


class Program(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "start_date",
            "end_date",
            "description",
            "ca_id",
            "ca_hash_id",
            "business_area",
            "budget",
            "frequency_of_payments",
            "sector",
            "scope",
            "cash_plus",
            "population_goal",
            "administrative_areas_of_implementation",
            "individual_data_needed",
        ],
        {"admin_areas_log": "admin_areas"},
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (ACTIVE, _("Active")),
        (DRAFT, _("Draft")),
        (FINISHED, _("Finished")),
    )

    REGULAR = "REGULAR"
    ONE_OFF = "ONE_OFF"

    FREQUENCY_OF_PAYMENTS_CHOICE = (
        (ONE_OFF, _("One-off")),
        (REGULAR, _("Regular")),
    )

    CHILD_PROTECTION = "CHILD_PROTECTION"
    EDUCATION = "EDUCATION"
    HEALTH = "HEALTH"
    MULTI_PURPOSE = "MULTI_PURPOSE"
    NUTRITION = "NUTRITION"
    SOCIAL_POLICY = "SOCIAL_POLICY"
    WASH = "WASH"

    SECTOR_CHOICE = (
        (CHILD_PROTECTION, _("Child Protection")),
        (EDUCATION, _("Education")),
        (HEALTH, _("Health")),
        (MULTI_PURPOSE, _("Multi Purpose")),
        (NUTRITION, _("Nutrition")),
        (SOCIAL_POLICY, _("Social Policy")),
        (WASH, _("WASH")),
    )

    SCOPE_FOR_PARTNERS = "FOR_PARTNERS"
    SCOPE_UNICEF = "UNICEF"

    SCOPE_CHOICE = (
        (SCOPE_FOR_PARTNERS, _("For partners")),
        (SCOPE_UNICEF, _("Unicef")),
    )

    name = CICharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        db_index=True,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    ca_id = CICharField(max_length=255, null=True, blank=True, db_index=True)
    ca_hash_id = CICharField(max_length=255, null=True, blank=True, db_index=True)
    admin_areas = models.ManyToManyField("geo.Area", related_name="programs", blank=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        validators=[MinValueValidator(Decimal("0.00"))],
        db_index=True,
    )
    frequency_of_payments = models.CharField(
        max_length=50,
        choices=FREQUENCY_OF_PAYMENTS_CHOICE,
    )
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE, db_index=True)
    scope = models.CharField(
        max_length=50,
        choices=SCOPE_CHOICE,
    )
    cash_plus = models.BooleanField()
    population_goal = models.PositiveIntegerField()
    administrative_areas_of_implementation = models.CharField(
        max_length=255,
        blank=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    individual_data_needed = models.BooleanField(
        default=False,
        help_text="""
        This boolean decides whether the target population sync will send
        all individuals of a household that's part of the population or only
        the relevant ones (collectors etc.)""",
    )
    data_collecting_type = models.ForeignKey(
        "core.DataCollectingType", related_name="programs", on_delete=models.PROTECT, null=True, blank=True
    )

    @staticmethod
    def get_total_number_of_households_from_payments(qs: Union[models.QuerySet, ExtendedQuerySetSequence]) -> int:
        return (
            qs.filter(**{"payment_items__delivered_quantity__gt": 0})
            .distinct("payment_items__household__unicef_id")
            .values_list("payment_items__household__unicef_id", flat=True)
            .order_by("payment_items__household__unicef_id")
            .count()
        )

    @property
    def total_number_of_households(self) -> int:
        qs = ExtendedQuerySetSequence(self.paymentplan_set.all(), self.cashplan_set.all())
        return self.get_total_number_of_households_from_payments(qs)

    @property
    def households_with_tp_in_program(self) -> QuerySet:
        target_populations_in_program = TargetPopulation.objects.filter(program=self).exclude(
            status=TargetPopulation.STATUS_OPEN
        )
        return Household.objects.filter(target_populations__in=target_populations_in_program).distinct()

    @property
    def admin_areas_log(self) -> str:
        return ", ".join(self.admin_areas.all())

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Programme"

    def __str__(self) -> str:
        return self.name


class ProgramCycle(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "iteration",
            "status",
            "start_date",
            "end_date",
            "description",
        ],
    )
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    STATUS_CHOICE = (
        (ACTIVE, _("Active")),
        (CLOSED, _("Closed")),
    )

    iteration = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        db_index=True,
        default=1,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")

    class Meta:
        unique_together = ("iteration", "program")
        ordering = ["program", "iteration"]
        verbose_name = "ProgrammeCycle"

    def __str__(self) -> str:
        return f"{self.program.name} - cycle {self.iteration}"
