import random
import time
from typing import Dict, List, Optional, Tuple

from django.contrib.gis.geos import Point

import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker
from pytz import utc

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    HUMANITARIAN_PARTNER,
    MARITAL_STATUS_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    RESIDENCE_STATUS_CHOICE,
    SEX_CHOICE,
    UNICEF,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)

faker = Faker()


class RegistrationDataImportDatahubFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImportDatahub

    factory.LazyFunction(
        lambda: f"{faker.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)} - {time.time_ns()}"
    )
    import_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        tzinfo=utc,
    )


class ImportedHouseholdFactory(DjangoModelFactory):
    class Meta:
        model = ImportedHousehold

    consent_sign = factory.django.ImageField(color="blue")
    consent = True
    consent_sharing = (UNICEF, HUMANITARIAN_PARTNER)
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    country = factory.LazyFunction(lambda: Country.objects.order_by("?").first().iso_code2)
    country_origin = factory.LazyFunction(lambda: Country.objects.order_by("?").first().iso_code2)
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory,
    )
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    admin1 = ""
    admin2 = ""
    admin3 = ""
    admin4 = ""
    admin1_title = ""
    admin2_title = ""
    admin3_title = ""
    admin4_title = ""
    geopoint = factory.LazyAttribute(lambda o: Point(faker.latlng()))
    female_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_18_59_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_60_count = factory.fuzzy.FuzzyInteger(3, 8)
    pregnant_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_18_59_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_60_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_18_59_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_60_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_18_59_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_60_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    start = factory.Faker("date_time_this_month", before_now=True, after_now=False, tzinfo=utc)
    deviceid = factory.Faker("md5")
    name_enumerator = factory.Faker("name")
    org_enumerator = factory.fuzzy.FuzzyChoice(
        ORG_ENUMERATOR_CHOICES,
        getter=lambda c: c[0],
    )
    org_name_enumerator = "Partner Organization"
    village = factory.Faker("city")
    enumerator_rec_id = factory.fuzzy.FuzzyInteger(9999999, 99999999)


class ImportedIndividualFactory(DjangoModelFactory):
    class Meta:
        model = ImportedIndividual

    full_name = factory.LazyAttribute(lambda o: f"{o.given_name} {o.middle_name} {o.family_name}")
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(
        SEX_CHOICE,
        getter=lambda c: c[0],
    )
    birth_date = factory.Faker("date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90)
    estimated_birth_date = factory.fuzzy.FuzzyChoice((True, False))
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    phone_no = factory.LazyFunction(faker.phone_number)
    phone_no_alternative = ""
    email = factory.Faker("email")
    registration_data_import = factory.SubFactory(RegistrationDataImportDatahubFactory)
    disability = False
    household = factory.SubFactory(ImportedHouseholdFactory)
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)


def create_imported_household(
    household_args: Optional[Dict] = None, individual_args: Optional[Dict] = None
) -> Tuple[ImportedHousehold, ImportedIndividual]:
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = ImportedHouseholdFactory(**household_args)
    individuals = ImportedIndividualFactory.create_batch(household.size, household=household, **individual_args)
    individuals[0].relationship = "HEAD"
    individuals[0].save()
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals


def create_imported_household_and_individuals(
    household_data: Optional[Dict] = None, individuals_data: Optional[List[Dict]] = None
) -> Tuple[ImportedHousehold, List[ImportedIndividual]]:
    if household_data is None:
        household_data = {}
    if individuals_data is None:
        individuals_data = []
    household: ImportedHousehold = ImportedHouseholdFactory.build(**household_data, size=len(individuals_data))
    individuals: List[ImportedIndividual] = [
        ImportedIndividualFactory(household=household, **individual_data) for individual_data in individuals_data
    ]
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals


class ImportedDocumentFactory(DjangoModelFactory):
    class Meta:
        model = ImportedDocument

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.LazyAttribute(lambda o: ImportedDocumentType.objects.order_by("?").first())
    individual = factory.SubFactory(ImportedIndividualFactory)


class ImportedDocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = ImportedDocumentType

    key = random.choice(["birth_certificate", "tax_id", "drivers_license"])


class ImportedBankAccountInfoFactory(DjangoModelFactory):
    class Meta:
        model = ImportedBankAccountInfo

    individual = factory.SubFactory(ImportedIndividualFactory)
    bank_name = random.choice(["CityBank", "Santander", "JPMorgan"])
    bank_account_number = random.randint(10**26, 10**27 - 1)
    bank_branch_name = random.choice(["BranchCityBank", "BranchSantander", "BranchJPMorgan"])
    account_holder_name = factory.Faker("last_name")
