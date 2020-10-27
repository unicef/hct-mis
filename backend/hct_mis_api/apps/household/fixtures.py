import random

import factory
from factory import fuzzy
from pytz import utc

from household.models import (
    HUMANITARIAN_PARTNER,
    MARITAL_STATUS_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SEX_CHOICE,
    UNICEF,
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from registration_data.fixtures import RegistrationDataImportFactory


def flex_field_households(o):
    return {
        "treatment_facility_h_f": random.sample(
            [
                "government_health_center",
                "governent_hospital",
                "other_public",
                "private_hospital",
                "pharmacy",
                "private_doctor",
                "other_private",
            ],
            k=2,
        ),
        "other_treatment_facility_h_f": random.choice(["testing other", "narodowy fundusz zdrowia", None]),
    }


def flex_field_individual(o):
    return {
        "seeing_disability_i_f": random.choice(["some_difficulty", "lot_difficulty", "cannot_do", None]),
        "hearing_disability_i_f": random.choice(["some_difficulty", "lot_difficulty", "cannot_do", None]),
        "physical_disability_i_f": random.choice(["some_difficulty", "lot_difficulty", "cannot_do", None]),
    }


class HouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = Household

    consent_sign = factory.django.ImageField(color="blue")
    consent = True
    consent_sharing = (UNICEF, HUMANITARIAN_PARTNER)
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    country_origin = factory.Faker("country_code")
    country = factory.Faker("country_code")
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportFactory,
    )
    first_registration_date = factory.Faker("date_this_year", before_today=True, after_today=False)
    last_registration_date = factory.Faker("date_this_year", before_today=True, after_today=False)
    flex_fields = factory.LazyAttribute(flex_field_households)
    business_area = factory.LazyAttribute(lambda o: o.registration_data_import.business_area)
    start = factory.Faker("date_this_month", before_today=True, after_today=False)
    end = factory.Faker("date_this_month", before_today=True, after_today=False)
    deviceid = factory.Faker("md5")
    name_enumerator = factory.Faker("name")
    org_enumerator = factory.fuzzy.FuzzyChoice(
        ORG_ENUMERATOR_CHOICES,
        getter=lambda c: c[0],
    )
    org_name_enumerator = "Partner Organization"
    village = factory.Faker("city")


class DocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Document

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.LazyAttribute(lambda o: DocumentType.objects.order_by("?").first())


class IndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = Individual

    full_name = factory.LazyAttribute(lambda o: f"{o.given_name} {o.middle_name} {o.family_name}")
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(
        SEX_CHOICE,
        getter=lambda c: c[0],
    )
    birth_date = factory.Faker("date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90)
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    relationship = factory.fuzzy.FuzzyChoice([value for value, label in RELATIONSHIP_CHOICE[1:] if value != "HEAD"])
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import = factory.SubFactory(RegistrationDataImportFactory)
    disability = False
    flex_fields = factory.LazyAttribute(flex_field_individual)
    first_registration_date = factory.Faker("date_this_year", before_today=True, after_today=False)
    last_registration_date = factory.Faker("date_this_year", before_today=True, after_today=False)


class EntitlementCardFactory(factory.DjangoModelFactory):
    class Meta:
        model = EntitlementCard

    card_number = factory.Faker("credit_card_number")
    status = fuzzy.FuzzyChoice(
        EntitlementCard.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    card_type = factory.Faker("credit_card_provider")
    current_card_size = "Lorem"
    card_custodian = factory.Faker("name")
    service_provider = factory.Faker("company")
    household = factory.SubFactory(HouseholdFactory)


def create_household(household_args=None, individual_args=None):
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(household.size, household=household, **individual_args)
    individuals[0].relationship = "HEAD"
    individuals[0].save()
    household.head_of_household = individuals[0]
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    household.save()
    primary_collector, alternate_collector = IndividualFactory.create_batch(
        2, household=None, relationship="NON_BENEFICIARY"
    )
    primary_collector_irh = IndividualRoleInHousehold(
        individual=primary_collector, household=household, role=ROLE_PRIMARY
    )
    primary_collector_irh.save()
    alternate_collector_irh = IndividualRoleInHousehold(
        individual=alternate_collector, household=household, role=ROLE_ALTERNATE
    )
    alternate_collector_irh.save()
    return household, individuals


def create_household_and_individuals(household_data=None, individuals_data=None, imported=False):
    if household_data is None:
        household_data = {}
    if individuals_data is None:
        individuals_data = {}
    household = HouseholdFactory.build(**household_data, size=len(individuals_data))
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    individuals = [IndividualFactory(household=household, **individual_data) for individual_data in individuals_data]
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals
