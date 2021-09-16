import logging
import re
from datetime import date, datetime

from django.contrib.gis.db.models import Count, PointField, Q, UniqueConstraint
from django.contrib.postgres.fields import CICharField, JSONField
from django.core.validators import MinLengthValidator, validate_image_file_extension
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from advanced_filters.admin import AdminAdvancedFiltersMixin
from dateutil.relativedelta import relativedelta
from django_countries.fields import CountryField
from model_utils import Choices
from model_utils.managers import SoftDeletableManager
from model_utils.models import SoftDeletableModel
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.geo.compat import GeoCountryField
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    ConcurrencyModel,
    SoftDeletableModelWithDate,
    TimeStampedUUIDModel,
)

BLANK = ""
IDP = "IDP"
REFUGEE = "REFUGEE"
OTHERS_OF_CONCERN = "OTHERS_OF_CONCERN"
HOST = "HOST"
NON_HOST = "NON_HOST"
RESIDENCE_STATUS_CHOICE = (
    (BLANK, _("None")),
    (IDP, _("Displaced  |  Internally Displaced People")),
    (REFUGEE, _("Displaced  |  Refugee / Asylum Seeker")),
    (OTHERS_OF_CONCERN, _("Displaced  |  Others of Concern")),
    (HOST, _("Non-displaced  |   Host")),
    (NON_HOST, _("Non-displaced  |   Non-host")),
)
# INDIVIDUALS
MALE = "MALE"
FEMALE = "FEMALE"
SEX_CHOICE = (
    (MALE, _("Male")),
    (FEMALE, _("Female")),
)
SINGLE = "SINGLE"
MARRIED = "MARRIED"
WIDOWED = "WIDOWED"
DIVORCED = "DIVORCED"
SEPARATED = "SEPARATED"
MARITAL_STATUS_CHOICE = (
    (BLANK, _("None")),
    (SINGLE, _("Single")),
    (MARRIED, _("Married")),
    (WIDOWED, _("Widowed")),
    (DIVORCED, _("Divorced")),
    (SEPARATED, _("Separated")),
)

NONE = "NONE"
SEEING = "SEEING"
HEARING = "HEARING"
WALKING = "WALKING"
MEMORY = "MEMORY"
SELF_CARE = "SELF_CARE"
COMMUNICATING = "COMMUNICATING"
OBSERVED_DISABILITY_CHOICE = (
    (NONE, _("None")),
    (SEEING, _("Difficulty seeing (even if wearing glasses)")),
    (HEARING, _("Difficulty hearing (even if using a hearing aid)")),
    (WALKING, _("Difficulty walking or climbing steps")),
    (MEMORY, _("Difficulty remembering or concentrating")),
    (SELF_CARE, _("Difficulty with self care (washing, dressing)")),
    (
        COMMUNICATING,
        _("Difficulty communicating " "(e.g understanding or being understood)"),
    ),
)
NON_BENEFICIARY = "NON_BENEFICIARY"
HEAD = "HEAD"
SON_DAUGHTER = "SON_DAUGHTER"
WIFE_HUSBAND = "WIFE_HUSBAND"
BROTHER_SISTER = "BROTHER_SISTER"
MOTHER_FATHER = "MOTHER_FATHER"
AUNT_UNCLE = "AUNT_UNCLE"
GRANDMOTHER_GRANDFATHER = "GRANDMOTHER_GRANDFATHER"
MOTHERINLAW_FATHERINLAW = "MOTHERINLAW_FATHERINLAW"
DAUGHTERINLAW_SONINLAW = "DAUGHTERINLAW_SONINLAW"
SISTERINLAW_BROTHERINLAW = "SISTERINLAW_BROTHERINLAW"
GRANDDAUGHER_GRANDSON = "GRANDDAUGHER_GRANDSON"
NEPHEW_NIECE = "NEPHEW_NIECE"
COUSIN = "COUSIN"
RELATIONSHIP_UNKNOWN = "UNKNOWN"
RELATIONSHIP_CHOICE = (
    (RELATIONSHIP_UNKNOWN, "Unknown"),
    (
        NON_BENEFICIARY,
        "Not a Family Member. Can only act as a recipient.",
    ),
    (HEAD, "Head of household (self)"),
    (SON_DAUGHTER, "Son / Daughter"),
    (WIFE_HUSBAND, "Wife / Husband"),
    (BROTHER_SISTER, "Brother / Sister"),
    (MOTHER_FATHER, "Mother / Father"),
    (AUNT_UNCLE, "Aunt / Uncle"),
    (GRANDMOTHER_GRANDFATHER, "Grandmother / Grandfather"),
    (MOTHERINLAW_FATHERINLAW, "Mother-in-law / Father-in-law"),
    (DAUGHTERINLAW_SONINLAW, "Daughter-in-law / Son-in-law"),
    (SISTERINLAW_BROTHERINLAW, "Sister-in-law / Brother-in-law"),
    (GRANDDAUGHER_GRANDSON, "Granddaughter / Grandson"),
    (NEPHEW_NIECE, "Nephew / Niece"),
    (COUSIN, "Cousin"),
)
YES = "1"
NO = "0"
YES_NO_CHOICE = (
    (BLANK, _("None")),
    (YES, _("Yes")),
    (NO, _("No")),
)
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
UNHCR = "UNHCR"
WFP = "WFP"
AGENCY_TYPE_CHOICES = (
    (UNHCR, _("UNHCR")),
    (WFP, _("WFP")),
)
STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"
STATUS_WITHDRAWN = "WITHDRAWN"
STATUS_DUPLICATE = "DUPLICATE"
INDIVIDUAL_STATUS_CHOICES = (
    (STATUS_ACTIVE, "Active"),
    (STATUS_WITHDRAWN, "Withdrawn"),
    (STATUS_DUPLICATE, "Duplicate"),
)
INDIVIDUAL_HOUSEHOLD_STATUS = ((STATUS_ACTIVE, "Active"), (STATUS_INACTIVE, "Inactive"))
UNIQUE = "UNIQUE"
DUPLICATE = "DUPLICATE"
NEEDS_ADJUDICATION = "NEEDS_ADJUDICATION"
NOT_PROCESSED = "NOT_PROCESSED"
DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE = (
    (UNIQUE, "Unique"),
    (DUPLICATE, "Duplicate"),
    (NEEDS_ADJUDICATION, "Needs Adjudication"),
    (NOT_PROCESSED, "Not Processed"),
)
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
SOME_DIFFICULTY = "SOME_DIFFICULTY"
LOT_DIFFICULTY = "LOT_DIFFICULTY"
CANNOT_DO = "CANNOT_DO"
SEVERITY_OF_DISABILITY_CHOICES = (
    (BLANK, _("None")),
    (SOME_DIFFICULTY, "Some difficulty"),
    (LOT_DIFFICULTY, "A lot of difficulty"),
    (CANNOT_DO, "Cannot do at all"),
)
UNICEF = "UNICEF"
PARTNER = "PARTNER"
ORG_ENUMERATOR_CHOICES = (
    (BLANK, _("None")),
    (UNICEF, "UNICEF"),
    (PARTNER, "Partner"),
)
HUMANITARIAN_PARTNER = "HUMANITARIAN_PARTNER"
PRIVATE_PARTNER = "PRIVATE_PARTNER"
GOVERNMENT_PARTNER = "GOVERNMENT_PARTNER"
DATA_SHARING_CHOICES = (
    (BLANK, _("None")),
    (UNICEF, "UNICEF"),
    (HUMANITARIAN_PARTNER, "Humanitarian partners"),
    (PRIVATE_PARTNER, "Private partners"),
    (GOVERNMENT_PARTNER, "Government partners"),
)
HH_REGISTRATION = "HH_REGISTRATION"
COMMUNITY = "COMMUNITY"
REGISTRATION_METHOD_CHOICES = (
    (BLANK, _("None")),
    (HH_REGISTRATION, "Household Registration"),
    (COMMUNITY, "Community-level Registration"),
)

DISABLED = "disabled"
NOT_DISABLED = "not disabled"
DISABILITY_CHOICES = (
    (
        DISABLED,
        "disabled",
    ),
    (
        NOT_DISABLED,
        "not disabled",
    ),
)
SANCTION_LIST_POSSIBLE_MATCH = "SANCTION_LIST_POSSIBLE_MATCH"
SANCTION_LIST_CONFIRMED_MATCH = "SANCTION_LIST_CONFIRMED_MATCH"
INDIVIDUAL_FLAGS_CHOICES = (
    (NEEDS_ADJUDICATION, "Needs adjudication"),
    (DUPLICATE, "Duplicate"),
    (SANCTION_LIST_POSSIBLE_MATCH, "Sanction list possible match"),
    (SANCTION_LIST_CONFIRMED_MATCH, "Sanction list match"),
)

logger = logging.getLogger(__name__)


class Household(SoftDeletableModelWithDate, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "withdrawn",
            "status",
            "consent_sign",
            "consent",
            "consent_sharing",
            "residence_status",
            "country_origin",
            "country",
            "size",
            "address",
            "admin_area",
            "representatives",
            "geopoint",
            "female_age_group_0_4_count",
            "female_age_group_5_12_count",
            "female_age_group_13_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_4_count",
            "male_age_group_5_12_count",
            "male_age_group_13_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_4_disabled_count",
            "female_age_group_5_12_disabled_count",
            "female_age_group_13_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_4_disabled_count",
            "male_age_group_5_12_disabled_count",
            "male_age_group_13_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "registration_data_import",
            "programs",
            "returnee",
            "flex_fields",
            "first_registration_date",
            "last_registration_date",
            "head_of_household",
            "fchild_hoh",
            "child_hoh",
            "unicef_id",
            "start",
            "deviceid",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
            "registration_method",
            "collect_individual_data",
            "currency",
            "unhcr_id",
        ]
    )
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    consent_sign = ImageField(validators=[validate_image_file_extension], blank=True)
    consent = models.NullBooleanField()
    consent_sharing = MultiSelectField(choices=DATA_SHARING_CHOICES, default=BLANK)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE)
    country_origin = CountryField(blank=True, db_index=True)
    country_origin_new = models.ForeignKey(
        "geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT
    )
    country = CountryField(db_index=True)
    country_new = models.ForeignKey("geo.Country", related_name="+", blank=True, null=True, on_delete=models.PROTECT)
    size = models.PositiveIntegerField(db_index=True)
    address = CICharField(max_length=255, blank=True)
    """location contains lowest administrative area info"""
    admin_area = models.ForeignKey("core.AdminArea", null=True, on_delete=models.SET_NULL, blank=True)
    representatives = models.ManyToManyField(
        to="household.Individual",
        through="household.IndividualRoleInHousehold",
        help_text="""This is only used to track collector (primary or secondary) of a household.
            They may still be a HOH of this household or any other household.
            Through model will contain the role (ROLE_CHOICE) they are connected with on.""",
        related_name="represented_households",
    )
    geopoint = PointField(blank=True, null=True)
    female_age_group_0_4_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_5_12_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_13_17_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    pregnant_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_4_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_5_12_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_13_17_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_0_4_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_5_12_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_13_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    female_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_0_4_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_5_12_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_13_17_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_18_59_disabled_count = models.PositiveIntegerField(default=None, null=True)
    male_age_group_60_disabled_count = models.PositiveIntegerField(default=None, null=True)
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="households",
        on_delete=models.CASCADE,
    )
    programs = models.ManyToManyField(
        "program.Program",
        related_name="households",
        blank=True,
    )
    returnee = models.NullBooleanField()
    flex_fields = JSONField(default=dict, blank=True)
    first_registration_date = models.DateTimeField()
    last_registration_date = models.DateTimeField()
    head_of_household = models.OneToOneField("Individual", related_name="heading_household", on_delete=models.CASCADE)
    fchild_hoh = models.NullBooleanField()
    child_hoh = models.NullBooleanField()
    unicef_id = CICharField(max_length=250, blank=True, default=BLANK, db_index=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    start = models.DateTimeField(blank=True, null=True)
    deviceid = models.CharField(max_length=250, blank=True, default=BLANK)
    name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    org_enumerator = models.CharField(max_length=250, choices=ORG_ENUMERATOR_CHOICES, default=BLANK)
    org_name_enumerator = models.CharField(max_length=250, blank=True, default=BLANK)
    village = models.CharField(max_length=250, blank=True, default=BLANK)
    registration_method = models.CharField(max_length=250, choices=REGISTRATION_METHOD_CHOICES, default=BLANK)
    collect_individual_data = models.CharField(max_length=250, choices=YES_NO_CHOICE, default=BLANK)
    currency = models.CharField(max_length=250, choices=CURRENCY_CHOICES, default=BLANK)
    unhcr_id = models.CharField(max_length=250, blank=True, default=BLANK, db_index=True)
    user_fields = JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Household"
        permissions = (("can_withdrawn", "Can withdrawn Household"),)

    def save(self, *args, **kwargs):
        from hct_mis_api.apps.targeting.models import HouseholdSelection

        if self.withdrawn:
            HouseholdSelection.objects.filter(household=self, target_population__status="APPROVED").delete()
        super().save(*args, **kwargs)

    @property
    def status(self):
        if self.withdrawn:
            return STATUS_INACTIVE
        return STATUS_ACTIVE

    def withdraw(self):
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()

    def set_sys_field(self, key, value):
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key):
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    @property
    def admin1(self):
        if self.admin_area is None:
            return None
        if self.admin_area.level == 0:
            return None
        current_admin = self.admin_area
        while current_admin.level != 1:
            current_admin = current_admin.parent
        return current_admin

    @property
    def admin2(self):
        if self.admin_area is None:
            return None
        if self.admin_area.level == 0:
            return None
        if self.admin_area.level == 1:
            return None
        current_admin = self.admin_area
        while current_admin.level != 2:
            current_admin = current_admin.parent
        return current_admin

    @property
    def sanction_list_possible_match(self):
        return self.individuals.filter(sanction_list_possible_match=True).count() > 0

    @property
    def sanction_list_confirmed_match(self):
        return self.individuals.filter(sanction_list_confirmed_match=True).count() > 0

    @property
    def total_cash_received(self):
        return self.payment_records.filter().aggregate(models.Sum("delivered_quantity")).get("delivered_quantity__sum")

    @property
    def total_cash_received_usd(self):
        return (
            self.payment_records.filter()
            .aggregate(models.Sum("delivered_quantity_usd"))
            .get("delivered_quantity_usd__sum")
        )

    @property
    def programs_with_delivered_quantity(self):
        programs = (
            self.payment_records.all()
            .annotate(program=F("cash_plan__program"))
            .values("program")
            .annotate(
                total_delivered_quantity=Sum("delivered_quantity"),
                total_delivered_quantity_usd=Sum("delivered_quantity_usd"),
                currency=F("currency"),
                program_name=F("cash_plan__program__name"),
                program_id=F("cash_plan__program__id"),
            )
            .order_by("cash_plan__program__created_at")
        )

        programs_dict = []

        for program in programs:
            programs_dict.append(
                {
                    "id": program["program_id"],
                    "name": program["program_name"],
                    "quantity": {
                        "total_delivered_quantity": program["total_delivered_quantity"],
                        "total_delivered_quantity_usd": program["total_delivered_quantity_usd"],
                        "currency": program["currency"],
                    },
                }
            )
        return programs_dict

    def __str__(self):
        return f"{self.unicef_id}"

    def recalculate_data(self):
        if not (self.collect_individual_data == YES):
            return
        for individual in self.individuals.all():
            individual.recalculate_data()
        date_5_years_ago = datetime.now() - relativedelta(years=+5)
        date_13_years_ago = datetime.now() - relativedelta(years=+13)
        date_18_years_ago = datetime.now() - relativedelta(years=+18)
        date_60_years_ago = datetime.now() - relativedelta(years=+60)

        is_beneficiary = ~Q(relationship=NON_BENEFICIARY)
        active_beneficiary = Q(withdrawn=False, duplicate=False)
        female_beneficiary = Q(Q(sex=FEMALE) & active_beneficiary & is_beneficiary)
        male_beneficiary = Q(Q(sex=MALE) & active_beneficiary & is_beneficiary)
        disabled_disability = Q(disability=DISABLED)
        female_disability_beneficiary = Q(disabled_disability & female_beneficiary)
        male_disability_beneficiary = Q(disabled_disability & male_beneficiary)

        to_5_years = Q(birth_date__gt=date_5_years_ago)
        from_5_to_13_years = Q(birth_date__lte=date_5_years_ago, birth_date__gt=date_13_years_ago)
        from_13_to_18_years = Q(birth_date__lte=date_13_years_ago, birth_date__gt=date_18_years_ago)
        from_18_to_60_years = Q(birth_date__lte=date_18_years_ago, birth_date__gt=date_60_years_ago)
        from_60_years = Q(birth_date__lte=date_60_years_ago)

        age_groups = self.individuals.aggregate(
            female_age_group_0_4_count=Count("id", distinct=True, filter=Q(female_beneficiary & to_5_years)),
            female_age_group_5_12_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_5_to_13_years)),
            female_age_group_13_17_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_13_to_18_years)),
            female_age_group_18_59_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_18_to_60_years)),
            female_age_group_60_count=Count("id", distinct=True, filter=Q(female_beneficiary & from_60_years)),
            male_age_group_0_4_count=Count("id", distinct=True, filter=Q(male_beneficiary & to_5_years)),
            male_age_group_5_12_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_5_to_13_years)),
            male_age_group_13_17_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_13_to_18_years)),
            male_age_group_18_59_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_18_to_60_years)),
            male_age_group_60_count=Count("id", distinct=True, filter=Q(male_beneficiary & from_60_years)),
            female_age_group_0_4_disabled_count=Count(
                "id", distinct=True, filter=Q(female_disability_beneficiary & to_5_years)
            ),
            female_age_group_5_12_disabled_count=Count(
                "id", distinct=True, filter=Q(female_disability_beneficiary & from_5_to_13_years)
            ),
            female_age_group_13_17_disabled_count=Count(
                "id", distinct=True, filter=Q(female_disability_beneficiary & from_13_to_18_years)
            ),
            female_age_group_18_59_disabled_count=Count(
                "id", distinct=True, filter=Q(female_disability_beneficiary & from_18_to_60_years)
            ),
            female_age_group_60_disabled_count=Count(
                "id", distinct=True, filter=Q(female_disability_beneficiary & from_60_years)
            ),
            male_age_group_0_4_disabled_count=Count(
                "id", distinct=True, filter=Q(male_disability_beneficiary & to_5_years)
            ),
            male_age_group_5_12_disabled_count=Count(
                "id", distinct=True, filter=Q(male_disability_beneficiary & from_5_to_13_years)
            ),
            male_age_group_13_17_disabled_count=Count(
                "id", distinct=True, filter=Q(male_disability_beneficiary & from_13_to_18_years)
            ),
            male_age_group_18_59_disabled_count=Count(
                "id", distinct=True, filter=Q(male_disability_beneficiary & from_18_to_60_years)
            ),
            male_age_group_60_disabled_count=Count(
                "id", distinct=True, filter=Q(male_disability_beneficiary & from_60_years)
            ),
            size=Count("id", distinct=True, filter=Q(is_beneficiary & active_beneficiary)),
            pregnant_count=Count("id", distinct=True, filter=Q(is_beneficiary & active_beneficiary & Q(pregnant=True))),
        )

        for key, value in age_groups.items():
            setattr(self, key, value)

        self.child_hoh = False
        self.fchild_hoh = False
        if self.head_of_household.age < 18:
            if self.head_of_household.sex == FEMALE:
                self.fchild_hoh = True
            self.child_hoh = True
        self.save()


class DocumentValidator(TimeStampedUUIDModel):
    type = models.ForeignKey("DocumentType", related_name="validators", on_delete=models.CASCADE)
    regex = models.CharField(max_length=100, default=".*")


class DocumentType(TimeStampedUUIDModel):
    country = CountryField(default="U")
    country_new = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)
    label = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)

    class Meta:
        unique_together = ("country", "type")

    def __str__(self):
        return f"{self.label} in {self.country}"


class Document(SoftDeletableModel, TimeStampedUUIDModel):
    document_number = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    individual = models.ForeignKey("Individual", related_name="documents", on_delete=models.CASCADE)
    type = models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)
    STATUS_PENDING = "PENDING"
    STATUS_VALID = "VALID"
    STATUS_NEED_INVESTIGATION = "NEED_INVESTIGATION"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_VALID, _("Valid")),
        (STATUS_NEED_INVESTIGATION, _("Need Investigation")),
        (STATUS_INVALID, _("Invalid")),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    objects = models.Manager()
    existing_objects = SoftDeletableManager()

    def clean(self):
        from django.core.exceptions import ValidationError

        for validator in self.type.validators.all():
            if not re.match(validator.regex, self.document_number):
                logger.error("Document number is not validating")
                raise ValidationError("Document number is not validating")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["document_number", "type"],
                condition=Q(Q(is_removed=False) & Q(status="VALID")),
                name="unique_if_not_removed_and_valid",
            )
        ]


class Agency(models.Model):
    type = models.CharField(max_length=100, choices=AGENCY_TYPE_CHOICES)
    label = models.CharField(
        max_length=100,
    )
    country = CountryField()
    country_new = models.ForeignKey("geo.Country", blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Agencies"
        constraints = [
            UniqueConstraint(
                fields=["type", "country"],
                name="unique_type_and_country",
            )
        ]

    def __str__(self):
        return self.label


class IndividualIdentity(models.Model):
    agency = models.ForeignKey("Agency", related_name="individual_identities", on_delete=models.CASCADE)
    individual = models.ForeignKey("Individual", related_name="identities", on_delete=models.CASCADE)
    number = models.CharField(
        max_length=255,
    )

    def __str__(self):
        return f"{self.agency} {self.individual} {self.number}"


class IndividualRoleInHousehold(TimeStampedUUIDModel, AbstractSyncable):
    individual = models.ForeignKey(
        "household.Individual",
        on_delete=models.CASCADE,
        related_name="households_and_roles",
    )
    household = models.ForeignKey(
        "household.Household",
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

    def __str__(self):
        return f"{self.individual.full_name} - {self.role}"


class Individual(SoftDeletableModelWithDate, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "duplicate",
            "withdrawn",
            "individual_id",
            "photo",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "household",
            "registration_data_import",
            "disability",
            "work_status",
            "first_registration_date",
            "last_registration_date",
            "flex_fields",
            "enrolled_in_nutrition_programme",
            "administration_of_rutf",
            "unicef_id",
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
            "imported_individual_id",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
            "sanction_list_last_check",
            "pregnant",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "who_answers_phone",
            "who_answers_alt_phone",
        ]
    )
    duplicate = models.BooleanField(default=False, db_index=True)
    duplicate_date = models.DateTimeField(null=True, blank=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True)
    individual_id = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(blank=True)
    full_name = CICharField(max_length=255, validators=[MinLengthValidator(2)], db_index=True)
    given_name = CICharField(max_length=85, blank=True, db_index=True)
    middle_name = CICharField(max_length=85, blank=True, db_index=True)
    family_name = CICharField(max_length=85, blank=True, db_index=True)
    sex = models.CharField(max_length=255, choices=SEX_CHOICE, db_index=True)
    birth_date = models.DateField(db_index=True)
    estimated_birth_date = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICE, default=BLANK, db_index=True)
    phone_no = PhoneNumberField(blank=True)
    phone_no_alternative = PhoneNumberField(blank=True)
    relationship = models.CharField(
        max_length=255,
        blank=True,
        choices=RELATIONSHIP_CHOICE,
        help_text="""This represents the MEMBER relationship. can be blank
            as well if household is null!""",
    )
    household = models.ForeignKey(
        "Household",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="""This represents the household this person is a MEMBER,
            and if null then relationship is NON_BENEFICIARY and that
            simply means they are a representative of one or more households
            and not a member of one.""",
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
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
    flex_fields = JSONField(default=dict, blank=True)
    user_fields = JSONField(default=dict, blank=True)
    enrolled_in_nutrition_programme = models.NullBooleanField()
    administration_of_rutf = models.NullBooleanField()
    unicef_id = CICharField(max_length=250, blank=True, db_index=True)
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    )
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
    )
    deduplication_golden_record_results = JSONField(default=dict, blank=True)
    deduplication_batch_results = JSONField(default=dict, blank=True)
    imported_individual_id = models.UUIDField(null=True, blank=True)
    sanction_list_possible_match = models.BooleanField(default=False)
    sanction_list_confirmed_match = models.BooleanField(default=False)
    sanction_list_last_check = models.DateTimeField(null=True, blank=True)
    pregnant = models.NullBooleanField()
    observed_disability = MultiSelectField(choices=OBSERVED_DISABILITY_CHOICE, default=NONE)
    seeing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    hearing_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    physical_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    memory_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    selfcare_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    comms_disability = models.CharField(max_length=50, choices=SEVERITY_OF_DISABILITY_CHOICES, blank=True)
    who_answers_phone = models.CharField(max_length=150, blank=True)
    who_answers_alt_phone = models.CharField(max_length=150, blank=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    fchild_hoh = models.BooleanField(default=False)
    child_hoh = models.BooleanField(default=False)

    @property
    def age(self):
        return relativedelta(date.today(), self.birth_date).years

    @property
    def role(self):
        role = self.households_and_roles.first()
        if role is not None:
            return role.role
        return ROLE_NO_ROLE

    @property
    def get_hash_key(self):
        from hashlib import sha256

        fields = (
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)) for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    @property
    def status(self):
        statuses = []
        if self.duplicate:
            statuses.append(STATUS_DUPLICATE)
        if self.withdrawn:
            statuses.append(STATUS_WITHDRAWN)
        if len(statuses) > 0:
            return ", ".join(statuses)
        return STATUS_ACTIVE

    @property
    def cash_assist_status(self):
        if self.withdrawn:
            return STATUS_INACTIVE
        if self.duplicate:
            return STATUS_INACTIVE
        return STATUS_ACTIVE

    def withdraw(self):
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()

    def mark_as_duplicate(self, original_individual=None):
        if original_individual is not None:
            self.unicef_id = original_individual.unicef_id
        self.documents.update(status=Document.STATUS_INVALID)
        self.duplicate = True
        self.duplicate_date = timezone.now()
        self.save()

    def __str__(self):
        return self.unicef_id

    class Meta:
        verbose_name = "Individual"

    def set_sys_field(self, key, value):
        if "sys" not in self.user_fields:
            self.user_fields["sys"] = {}
        self.user_fields["sys"][key] = value

    def get_sys_field(self, key):
        if "sys" in self.user_fields:
            return self.user_fields["sys"][key]
        return None

    def recalculate_data(self):
        disability_fields = (
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
        )
        should_be_disabled = False
        for field in disability_fields:
            value = getattr(self, field, None)
            should_be_disabled = should_be_disabled or value == CANNOT_DO or value == LOT_DIFFICULTY
        self.disability = DISABLED if should_be_disabled else NOT_DISABLED
        self.save()

    def count_all_roles(self):
        return self.households_and_roles.exclude(role=ROLE_NO_ROLE).count()

    @cached_property
    def parents(self):
        if self.household:
            return self.household.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True))
        return []

    def is_golden_record_duplicated(self):
        return self.deduplication_golden_record_status == DUPLICATE

    def get_deduplication_golden_record(self):
        status_key = "duplicates" if self.is_golden_record_duplicated() else "possible_duplicates"
        return self.deduplication_golden_record_results.get(status_key, [])

    @cached_property
    def active_record(self):
        if self.duplicate:
            return Individual.objects.filter(unicef_id=self.unicef_id, duplicate=False, is_removed=False).first()


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
        choices=STATUS_CHOICE,
        default=ACTIVE,
        max_length=10,
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
