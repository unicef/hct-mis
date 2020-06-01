from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from household.models import (
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    MARITAL_STATUS_CHOICE,
    INDIVIDUAL_HOUSEHOLD_STATUS,
)
from utils.models import AbstractSession


class Session(AbstractSession):
    pass


class SessionModel(models.Model):
    session_id = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Household(SessionModel):
    mis_id = models.UUIDField(primary_key=True,)
    status = models.CharField(
        max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE"
    )
    household_size = models.PositiveIntegerField()
    # head of household document id
    government_form_number = models.CharField(max_length=255, null=True)
    # registration household id
    form_number = models.CharField(max_length=255, null=True)
    agency_id = models.CharField(max_length=255, null=True)
    #  individual_id head of household
    focal_point = models.ForeignKey(
        "mis_datahub.Individual",
        db_column="focal_point_mis_id",
        on_delete=models.CASCADE,
        related_name="heading_household",
    )
    address = models.CharField(max_length=255, null=True)
    admin1 = models.CharField(max_length=255, null=True)
    admin2 = models.CharField(max_length=255, null=True)
    country = CountryField(null=True)


class Individual(SessionModel):
    mis_id = models.UUIDField(primary_key=True,)
    household = models.ForeignKey(
        "mis_datahub.Household",
        db_column="household_mis_id",
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
    mis_id = models.UUIDField(primary_key=True,)
    name = models.CharField(max_length=255)
    population_type = models.CharField(default="HOUSEHOLD", max_length=20)
    targeting_criteria = models.TextField()

    active_households = models.PositiveIntegerField(default=0)
    program = models.ForeignKey(
        "mis_datahub.Program",
        db_column="program_mis_id",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class TargetPopulationEntry(SessionModel):

    target_population = models.ForeignKey(
        "mis_datahub.TargetPopulation",
        on_delete=models.CASCADE,
        db_column="target_population_mis_id",
    )
    household = models.ForeignKey(
        "mis_datahub.Household",
        on_delete=models.CASCADE,
        null=True,
        db_column="household_mis_id",
    )
    individual = models.ForeignKey(
        "mis_datahub.Individual",
        on_delete=models.CASCADE,
        null=True,
        db_column="individual_mis_id",
    )
    ca_household_id = models.CharField(max_length=255)
    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )


class Program(SessionModel):
    STATUS_NOT_STARTED = "NOT_STARTED"
    STATUS_STARTED = "STARTED"
    STATUS_COMPLETE = "COMPLETE"
    SCOPE_FOR_PARTNERS = "FOR_PARTNERS"
    SCOPE_UNICEF = "UNICEF"
    STATUS_CHOICE = (
        (STATUS_NOT_STARTED, _("NOT_STARTED")),
        (STATUS_STARTED, _("STARTED")),
        (STATUS_COMPLETE, _("COMPLETE")),
    )
    SCOPE_CHOICE = (
        (SCOPE_FOR_PARTNERS, _("For partners")),
        (SCOPE_UNICEF, _("Unicef")),
    )
    mis_id = models.UUIDField(primary_key=True,)
    business_area = models.CharField(max_length=20)
    ca_id = models.CharField(max_length=255)
    ca_hash_id = models.CharField(max_length=255)
    programme_name = models.CharField(max_length=255)
    scope = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255, null=True)
