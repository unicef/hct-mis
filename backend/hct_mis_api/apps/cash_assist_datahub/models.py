from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices

from household.models import (
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    MARITAL_STATUS_CHOICE,
    INDIVIDUAL_HOUSEHOLD_STATUS,
)


class Session(models.Model):
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


class SessionModel(models.Model):
    session_id = models.ForeignKey(
        "cash_assist_datahub.Session", on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class Household(SessionModel):
    status = models.CharField(
        max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE"
    )
    household_id = models.UUIDField(primary_key=True,)
    status = models.CharField(
        max_length=50, choices=(("INACTIVE", "Inactive"), ("ACTIVE", "Active")),
    )
    household_size = models.PositiveIntegerField()
    # head of household document id
    government_form_number = models.CharField(max_length=255, null=True)
    # registration household id
    form_number = models.CharField(max_length=255, null=True)
    agency_id = models.CharField(max_length=255, null=True)
    #  individual_id head of household
    focal_point = models.ForeignKey(
        "cash_assist_datahub.Individual",
        db_column="focal_point",
        on_delete=models.CASCADE,
        related_name="heading_household",
    )
    address = models.CharField(max_length=255, null=True)
    admin1 = models.CharField(max_length=255, null=True)
    admin2 = models.CharField(max_length=255, null=True)
    country = CountryField(null=True)


class Individual(SessionModel):
    individual_id = models.UUIDField(primary_key=True,)
    household = models.ForeignKey(
        "cash_assist_datahub.Household",
        db_column="household_id",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=50,
        choices=(("INACTIVE", "Inactive"), ("ACTIVE", "Active")),
        null=True,
    )
    SEX_CHOICE = (
        ("MALE", _("Male")),
        ("FEMALE", _("Female")),
    )
    full_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255, null=True)
    given_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    date_of_birth = models.DateField()
    estimated_date_of_birth = models.BooleanField()
    relationship = models.CharField(
        max_length=255, null=True, choices=RELATIONSHIP_CHOICE,
    )
    role = models.CharField(max_length=255, null=True, choices=ROLE_CHOICE,)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICE,
    )
    phone_number = models.CharField(max_length=14, null=True)

    def __str__(self):
        return self.family_name


class TargetPopulation(SessionModel):
    tp_unicef_id = models.UUIDField(primary_key=True,)
    name = models.CharField(max_length=255)
    population_type = models.CharField(default="HOUSEHOLD", max_length=20)
    targeting_criteria = models.TextField()

    active_households = models.PositiveIntegerField(default=0)
    program = models.ForeignKey(
        "cash_assist_datahub.Program",
        db_column="program_id",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class TargetPopulationEntry(SessionModel):
    target_population = models.ForeignKey(
        "cash_assist_datahub.TargetPopulation", on_delete=models.CASCADE,
    )
    household = models.ForeignKey(
        "cash_assist_datahub.Household", on_delete=models.CASCADE, null=True
    )
    individual = models.ForeignKey(
        "cash_assist_datahub.Individual", on_delete=models.CASCADE, null=True
    )
    unhcr_household_id = models.CharField(max_length=255)
    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )


class Program(SessionModel):
    program_id = models.UUIDField(primary_key=True,)
    business_area = models.CharField(max_length=20)
    STATUS_CHOICE = (
        ("NOT_STARTED", _("NOT_STARTED")),
        ("STARTED", _("STARTED")),
        ("COMPLETE", _("COMPLETE")),
    )
    SCOPE_CHOICE = (
        ("FOR_PARTNERS", _("For partners")),
        ("UNICEF", _("Unicef")),
    )
    program_unhcr_id = models.CharField(max_length=255)
    program_hash_id = models.CharField(max_length=255)
    programme_name = models.CharField(max_length=255)
    scope = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255, null=True)


class CashPlan(SessionModel):
    business_area = models.CharField(max_length=20)
    cash_plan_id = models.CharField(max_length=255)
    cash_plan_hash_id = models.UUIDField(primary_key=True,)
    status = models.CharField(
        max_length=255,
        choices=(
            ("Distribution Completed", "Distribution Completed"),
            (
                "Distribution Completed with Errors",
                "Distribution Completed with Errors",
            ),
            ("Transaction Completed", "Transaction Completed"),
            (
                "Transaction Completed with Errors",
                "Transaction Completed with Errors",
            ),
        ),
    )
    status_date = models.DateTimeField()
    name = models.CharField(max_length=255)
    distribution_level = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    dispersion_date = models.DateTimeField()
    coverage_duration = models.PositiveIntegerField()
    coverage_unit = models.CharField(max_length=255)
    comments = models.CharField(max_length=255)
    program = models.ForeignKey(
        "Program", on_delete=models.CASCADE, related_name="cash_plans"
    )
    delivery_type = models.CharField(max_length=255)
    assistance_measurement = models.CharField(max_length=255)
    assistance_through = models.CharField(max_length=255)
    vision_id = models.CharField(max_length=255)
    funds_commitment = models.CharField(max_length=255)
    down_payment = models.CharField(max_length=255)
    validation_alerts_count = models.IntegerField()
    total_persons_covered = models.IntegerField()
    total_persons_covered_revised = models.IntegerField()
    payment_records_count = models.IntegerField()
    total_entitled_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_entitled_quantity_revised = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_undelivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )


class PaymentRecord(SessionModel):
    STATUS_CHOICE = (
        ("SUCCESS", _("Sucess")),
        ("PENDING", _("Pending")),
        ("ERROR", _("Error")),
    )
    ENTITLEMENT_CARD_STATUS_CHOICE = Choices(
        ("ACTIVE", _("Active")), ("INACTIVE", _("Inactive")),
    )
    DELIVERY_TYPE_CHOICE = (
        ("CASH", _("Cash")),
        ("DEPOSIT_TO_CARD", _("Deposit to Card")),
        ("TRANSFER", _("Transfer")),
    )
    business_area = models.CharField(max_length=20)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE,)
    status_date = models.DateTimeField()
    payment_id = models.CharField(max_length=255)
    payment_hash_id = models.UUIDField(primary_key=True,)
    cash_plan = models.ForeignKey(
        "cash_assist_datahub.CashPlan", on_delete=models.CASCADE, related_name="payment_records",
    )
    unhcr_registration_id = models.CharField(max_length=255)
    household = models.ForeignKey(
        "cash_assist_datahub.Household", on_delete=models.CASCADE, related_name="payment_records",
    )
    # head of household
    focal_point = models.ForeignKey(
        "cash_assist_datahub.Individual", on_delete=models.CASCADE, related_name="payment_records",
    )
    full_name = models.CharField(max_length=255)
    total_persons_covered = models.IntegerField()
    distribution_modality = models.CharField(max_length=255,)
    target_population = models.ForeignKey(
        "TargetPopulation",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )
    target_population_cash_assist_id = models.CharField(max_length=255)
    entitlement_card_number = models.CharField(max_length=255,)
    entitlement_card_status = models.CharField(
        choices=STATUS_CHOICE, default="ACTIVE", max_length=20,
    )
    entitlement_card_issue_date = models.DateField()
    delivery_type = models.CharField(
        choices=DELIVERY_TYPE_CHOICE, default="ACTIVE", max_length=20,
    )
    currency = models.CharField(max_length=4,)
    entitlement_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivered_quantity = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    delivery_date = models.DateTimeField()
    service_provider = models.ForeignKey(
        "ServiceProvider",
        on_delete=models.CASCADE,
        related_name="payment_records",
    )


class ServiceProvider(SessionModel):
    business_area = models.CharField(max_length=20)
    id = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=4)
    country = models.CharField(max_length=3,)
    vision_id = models.CharField(max_length=255)
