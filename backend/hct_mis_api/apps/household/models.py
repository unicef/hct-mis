import re
from datetime import date

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from utils.models import TimeStampedUUIDModel, AbstractSyncable

RESIDENCE_STATUS_CHOICE = (
    ("REFUGEE", _("Refugee")),
    ("MIGRANT", _("Migrant")),
    ("CITIZEN", _("Citizen")),
    ("IDP", _("IDP")),
    ("OTHER", _("Other")),
)
# INDIVIDUALS
SEX_CHOICE = (
    ("MALE", _("Male")),
    ("FEMALE", _("Female")),
)
MARITAL_STATUS_CHOICE = (
    ("SINGLE", _("SINGLE")),
    ("MARRIED", _("Married")),
    ("WIDOW", _("Widow")),
    ("DIVORCED", _("Divorced")),
    ("SEPARATED", _("Separated")),
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
RELATIONSHIP_CHOICE = (
    ("NON_BENEFICIARY", "Not a Family Member. Can only act as a recipient.",),
    ("HEAD", "Head of household (self)"),
    ("SON_DAUGHTER", "Son / Daughter"),
    ("WIFE_HUSBAND", "Wife / Husband"),
    ("BROTHER_SISTER", "Brother / Sister"),
    ("MOTHER_FATHER", "Mother / Father"),
    ("AUNT_UNCLE", "Aunt / Uncle"),
    ("GRANDMOTHER_GRANDFATHER", "Grandmother / Grandfather"),
    ("MOTHERINLAW_FATHERINLAW", "Mother-in-law / Father-in-law"),
    ("DAUGHTERINLAW_SONINLAW", "Daughter-in-law / Son-in-law"),
    ("SISTERINLAW_BROTHERINLAW", "Sister-in-law / Brother-in-law"),
    ("GRANDDAUGHER_GRANDSON", "Granddaughter / Grandson"),
    ("NEPHEW_NIECE", "Nephew / Niece"),
    ("COUSIN", "Cousin"),
)
YES = "YES"
NO = "NO"
NOT_PROVIDED = "NOT_PROVIDED"
WORK_STATUS_CHOICE = (
    (YES, _("Yes")),
    (NO, _("No")),
    (NOT_PROVIDED, _("Not provided")),
)
ROLE_PRIMARY = "PRIMARY"
ROLE_ALTERNATE = "ALTERNATE"
ROLE_NO_ROLE = "NO_ROLE"
ROLE_CHOICE = (
    (ROLE_PRIMARY, "Primary collector"),
    (ROLE_ALTERNATE, "Alternate collector"),
    (ROLE_NO_ROLE, "None"),
)
IDENTIFICATION_TYPE_BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
IDENTIFICATION_TYPE_DRIVERS_LICENSE = "DRIVERS_LICENSE"
IDENTIFICATION_TYPE_NATIONAL_ID = "NATIONAL_ID"
IDENTIFICATION_TYPE_NATIONAL_PASSPORT = "NATIONAL_PASSPORT"
IDENTIFICATION_TYPE_ELECTORAL_CARD = "ELECTORAL_CARD"
IDENTIFICATION_TYPE_OTHER = "OTHER"
IDENTIFICATION_TYPE_CHOICE = (
    (IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, _("Birth Certificate")),
    (IDENTIFICATION_TYPE_DRIVERS_LICENSE, _("Driver's License")),
    (IDENTIFICATION_TYPE_NATIONAL_ID, _("National ID")),
    (IDENTIFICATION_TYPE_NATIONAL_PASSPORT, _("National Passport")),
    (IDENTIFICATION_TYPE_ELECTORAL_CARD, _("Electoral Card")),
    (IDENTIFICATION_TYPE_OTHER, _("Other")),
)
IDENTIFICATION_TYPE_DICT = {
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: "Birth Certificate",
    IDENTIFICATION_TYPE_DRIVERS_LICENSE: "Driver's License",
    IDENTIFICATION_TYPE_NATIONAL_ID: "National ID",
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT: "National Passport",
    IDENTIFICATION_TYPE_ELECTORAL_CARD: "Electoral Card",
    IDENTIFICATION_TYPE_OTHER: "Other",
}
INDIVIDUAL_HOUSEHOLD_STATUS = (("ACTIVE", "Active"), ("INACTIVE", "Inactive"))


class Household(TimeStampedUUIDModel, AbstractSyncable):
    status = models.CharField(
        max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE"
    )

    consent = ImageField(validators=[validate_image_file_extension])
    residence_status = models.CharField(
        max_length=255, choices=RESIDENCE_STATUS_CHOICE,
    )
    country_origin = CountryField(blank=True)
    country = CountryField(blank=True)

    size = models.PositiveIntegerField()
    address = models.CharField(max_length=255, blank=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey(
        "core.AdminArea", null=True, on_delete=models.SET_NULL
    )
    geopoint = PointField(blank=True, null=True)
    female_age_group_0_5_count = models.PositiveIntegerField(default=0)
    female_age_group_6_11_count = models.PositiveIntegerField(default=0)
    female_age_group_12_17_count = models.PositiveIntegerField(default=0)
    female_adults_count = models.PositiveIntegerField(default=0)
    pregnant_count = models.PositiveIntegerField(default=0)
    male_age_group_0_5_count = models.PositiveIntegerField(default=0)
    male_age_group_6_11_count = models.PositiveIntegerField(default=0)
    male_age_group_12_17_count = models.PositiveIntegerField(default=0)
    male_adults_count = models.PositiveIntegerField(default=0)
    female_age_group_0_5_disabled_count = models.PositiveIntegerField(default=0)
    female_age_group_6_11_disabled_count = models.PositiveIntegerField(
        default=0
    )
    female_age_group_12_17_disabled_count = models.PositiveIntegerField(
        default=0
    )
    female_adults_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_0_5_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_6_11_disabled_count = models.PositiveIntegerField(default=0)
    male_age_group_12_17_disabled_count = models.PositiveIntegerField(default=0)
    male_adults_disabled_count = models.PositiveIntegerField(default=0)
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program", related_name="households", blank=True,
    )
    returnee = models.BooleanField(default=False, null=True)
    flex_fields = JSONField(default=dict)
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    head_of_household = models.OneToOneField(
        "Individual",
        related_name="heading_household",
        on_delete=models.CASCADE,
    )
    unicef_id = models.CharField(max_length=250, blank=True)

    @property
    def total_cash_received(self):
        return (
            self.payment_records.filter()
            .aggregate(Sum("delivered_quantity"))
            .get("delivered_quantity__sum")
        )

    @property
    def business_area(self):
        return self.admin_area.admin_area_type.business_area

    def __str__(self):
        return f"Household ID: {self.id}"


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey(
        "DocumentType", related_name="validators", on_delete=models.CASCADE
    )
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(blank=True)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label} in {self.country}"


class Document(TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey(
        "Individual", related_name="documents", on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        "DocumentType", related_name="documents", on_delete=models.CASCADE
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators:
            if not re.match(validator.regex, self.document_number):
                raise ValidationError("Document number is not validating")

    class Meta:
        unique_together = ("type", "document_number")


class Agency(models.Model):
    type = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100,)

    def __str__(self):
        return self.label


class HouseholdIdentity(models.Model):
    agency = models.ForeignKey(
        "Agency", related_name="households_identities", on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "Household", related_name="identities", on_delete=models.CASCADE
    )
    document_number = models.CharField(max_length=255,)

    def __str__(self):
        return f"{self.agency} {self.individual} {self.document_number}"


class IndividualIdentity(models.Model):
    agency = models.ForeignKey(
        "Agency", related_name="individual_identities", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "Individual", related_name="identities", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=255,)

    class Meta:
        unique_together = ("agency", "number")

    def __str__(self):
        return f"{self.agency} {self.individual} {self.number}"


class Individual(TimeStampedUUIDModel, AbstractSyncable):
    status = models.CharField(
        max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE"
    )
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    given_name = models.CharField(max_length=85, blank=True,)
    middle_name = models.CharField(max_length=85, blank=True,)
    family_name = models.CharField(max_length=85, blank=True,)
    relationship = models.CharField(
        max_length=255, blank=True, choices=RELATIONSHIP_CHOICE,
    )
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE,)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE,)
    birth_date = models.DateField()
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICE,
    )
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    household = models.ForeignKey(
        "Household", related_name="individuals", on_delete=models.CASCADE,
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
    )
    disability = models.BooleanField(default=False,)
    work_status = models.CharField(
        max_length=20,
        choices=WORK_STATUS_CHOICE,
        blank=True,
        default=NOT_PROVIDED,
    )
    first_registration_date = models.DateField()
    last_registration_date = models.DateField()
    flex_fields = JSONField(default=dict)
    enrolled_in_nutrition_programme = models.BooleanField(default=False)
    administration_of_rutf = models.BooleanField(default=False)
    unicef_id = models.CharField(max_length=250, blank=True)

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - (
                (today.month, today.day)
                < (self.birth_date.month, self.birth_date.day)
            )
        )

    def __str__(self):
        return self.full_name


class EntitlementCard(TimeStampedUUIDModel):
    ACTIVE = "ACTIVE"
    ERRONEOUS = "ERRONEOUS"
    CLOSED = "CLOSED"
    STATUS_CHOICE = Choices(
        (ACTIVE, _("Active")),
        (ERRONEOUS, _("Erroneous")),
        (CLOSED, _("Closed")),
    )
    card_number = models.CharField(max_length=255)
    status = models.CharField(
        choices=STATUS_CHOICE, default=ACTIVE, max_length=10,
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
