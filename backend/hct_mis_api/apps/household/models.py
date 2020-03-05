from datetime import date

from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from household.const import NATIONALITIES
from utils.models import TimeStampedUUIDModel


class Household(TimeStampedUUIDModel):
    RESIDENCE_STATUS_CHOICE = (
        ("REFUGEE", _("Refugee")),
        ("MIGRANT", _("Migrant")),
        ("CITIZEN", _("Citizen")),
        ("IDP", _("IDP")),
        ("OTHER", _("Other")),
    )

    household_ca_id = models.CharField(max_length=255)
    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    nationality = models.CharField(max_length=255, choices=NATIONALITIES,)
    family_size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(
        "core.Location", related_name="households", on_delete=models.CASCADE,
    )
    representative = models.ForeignKey(
        "Individual",
        on_delete=models.SET_NULL,
        related_name="represented_households",
        null=True,
    )
    registration_data_import_id = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    head_of_household = models.OneToOneField(
        "Individual",
        on_delete=models.CASCADE,
        related_name="heading_household",
        null=True,
    )
    registration_date = models.DateField(null=True)

    @property
    def total_cash_received(self):
        return (
            self.payment_records.filter()
            .aggregate(Sum("entitlement__delivered_quantity"))
            .get("entitlement__delivered_quantity__sum")
        )

    def __str__(self):
        return f"Household CashAssist ID: {self.household_ca_id}"


class Individual(TimeStampedUUIDModel):
    SEX_CHOICE = (
        ("MALE", _("Male")),
        ("FEMALE", _("Female")),
    )
    MARTIAL_STATUS_CHOICE = (
        ("SINGLE", _("SINGLE")),
        ("MARRIED", _("Married")),
        ("WIDOW", _("Widow")),
        ("DIVORCED", _("Divorced")),
        ("SEPARATED", _("Separated")),
    )
    IDENTIFICATION_TYPE_CHOICE = (
        ("NA", _("N/A")),
        ("BIRTH_CERTIFICATE", _("Birth Certificate")),
        ("DRIVING_LICENSE", _("Driving License")),
        ("UNHCR_ID_CARD", _("UNHCR ID card")),
        ("NATIONAL_ID", _("National ID")),
        ("NATIONAL_PASSPORT", _("National Passport")),
    )
    YES_NO_CHOICE = (
        ("YES", _("Yes")),
        ("NO", _("No")),
    )
    DISABILITY_CHOICE = (
        ("NO", _("No")),
        ("SEEING", _("Difficulty seeing (even if wearing glasses)")),
        ("HEARING", _("Difficulty hearing (even if using a hearing aid)")),
        ("WALKING", _("Difficulty walking or climbing steps")),
        ("MEMORY", _("Difficulty remembering or concentrating")),
        ("SELF_CARE", _("Difficulty with self care (washing, dressing)")),
        (
            "COMMUNICATING",
            _(
                "Difficulty communicating "
                "(e.g understanding or being understood)"
            ),
        ),
    )

    individual_ca_id = models.CharField(max_length=255)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    first_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
    )
    middle_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
        blank=True,
    )
    last_name = models.CharField(
        max_length=85,
        validators=[MinLengthValidator(3), MaxLengthValidator(85)],
    )
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    dob = models.DateField(blank=True, null=True)
    estimated_dob = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=255, choices=NATIONALITIES,)
    martial_status = models.CharField(
        max_length=255, choices=MARTIAL_STATUS_CHOICE,
    )
    phone_number = PhoneNumberField(blank=True)
    phone_number_alternative = PhoneNumberField(blank=True)
    identification_type = models.CharField(
        max_length=255, choices=IDENTIFICATION_TYPE_CHOICE,
    )
    identification_number = models.CharField(max_length=255)
    household = models.ForeignKey(
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import_id = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    work_status = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    disability = models.CharField(
        max_length=30, default="NO", choices=DISABILITY_CHOICE,
    )
    serious_illness = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    age_first_married = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_school = models.CharField(
        max_length=3, default="NO", choices=YES_NO_CHOICE,
    )
    school_attendance = models.CharField(max_length=100, blank=True, default="")
    school_type = models.CharField(max_length=100, blank=True, default="")
    years_in_school = models.PositiveIntegerField(null=True, default=None)
    minutes_to_school = models.PositiveIntegerField(null=True, default=None)
    enrolled_in_nutrition_programme = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
    )
    administration_of_rutf = models.CharField(
        max_length=3, default="", choices=YES_NO_CHOICE, blank=True,
    )

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.dob.year
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    def __str__(self):
        return self.full_name


class EntitlementCard(TimeStampedUUIDModel):
    STATUS_CHOICE = Choices(
        ("ACTIVE", _("Active")),
        ("ERRONEOUS", _("Erroneous")),
        ("CLOSED", _("Closed")),
    )
    card_number = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICE, default=STATUS_CHOICE.ACTIVE, max_length=10,
    )
    card_type = models.CharField(max_length=255)
    current_card_size = models.CharField(max_length=255)
    card_custodian = models.CharField(max_length=255)
    service_provider = models.CharField(max_length=255)
    household = models.ForeignKey(
        "Household",
        related_name="entitlement_cards",
        on_delete=models.SET_NULL,
        null=True,
    )
