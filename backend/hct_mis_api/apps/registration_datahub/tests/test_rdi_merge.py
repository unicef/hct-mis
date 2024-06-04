from contextlib import contextmanager
from typing import Callable, Generator

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections
from django.forms import model_to_dict

import pytest
from freezegun import freeze_time
from parameterized import parameterized

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    BROTHER_SISTER,
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_PARTIAL,
    COUSIN,
    HEAD,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    Household,
    Individual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedHouseholdFactory,
    ImportedIndividualFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
)
from hct_mis_api.apps.registration_datahub.tasks.rdi_merge import RdiMergeTask


@contextmanager
def capture_on_commit_callbacks(
    *, using: str = DEFAULT_DB_ALIAS, execute: bool = False
) -> Generator[list[Callable[[], None]], None, None]:
    callbacks: list[Callable[[], None]] = []
    start_count = len(connections[using].run_on_commit)
    try:
        yield callbacks
    finally:
        while True:
            callback_count = len(connections[using].run_on_commit)
            for _, callback in connections[using].run_on_commit[start_count:]:
                callbacks.append(callback)
                if execute:
                    callback()

            if callback_count == len(connections[using].run_on_commit):
                break
            start_count = callback_count


class TestRdiMergeTask(BaseElasticSearchTestCase):
    databases = {"default", "registration_datahub"}
    fixtures = [
        f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",
        f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json",
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        program = ProgramFactory()
        cls.rdi = RegistrationDataImportFactory(program=program)
        cls.rdi.business_area.postpone_deduplication = True
        cls.rdi.business_area.save()
        cls.rdi_hub = RegistrationDataImportDatahubFactory(
            name=cls.rdi.name, hct_id=cls.rdi.id, business_area_slug=cls.rdi.business_area.slug
        )
        cls.rdi.datahub_id = cls.rdi_hub.id
        cls.rdi.save()

        area_type_level_1 = AreaTypeFactory(
            name="State1",
            area_level=1,
        )
        area_type_level_2 = AreaTypeFactory(
            name="State2",
            area_level=2,
        )
        area_type_level_3 = AreaTypeFactory(
            name="State3",
            area_level=3,
        )
        area_type_level_4 = AreaTypeFactory(
            name="State4",
            area_level=4,
        )
        cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
        cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
        cls.area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code="area3", parent=cls.area2)
        cls.area4 = AreaFactory(name="City Test4", area_type=area_type_level_4, p_code="area4", parent=cls.area3)

        super().setUpTestData()

    @classmethod
    def set_imported_individuals(cls, imported_household: ImportedHouseholdFactory) -> None:
        individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "relationship": HEAD,
                "birth_date": "1962-02-02",  # age 39
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "fake_email_1@com",
                "wallet_name": "Wallet Name 1",
                "blockchain_name": "Blockchain Name 1",
                "wallet_address": "Wallet Address 1",
                "mis_unicef_id": "IND-9",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "relationship": COUSIN,
                "birth_date": "2017-02-15",  # age 4
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "fake_email_2@com",
                "mis_unicef_id": "IND-8",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "relationship": COUSIN,
                "birth_date": "2011-12-21",  # age 10
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "fake_email_3@com",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "relationship": BROTHER_SISTER,
                "birth_date": "2006-03-23",  # age 15
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "fake_email_4@com",
            },
            {
                "full_name": "Baz Bush",
                "given_name": "Baz",
                "family_name": "Bush",
                "relationship": BROTHER_SISTER,
                "birth_date": "2005-02-21",  # age 16
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "fake_email_5@com",
            },
            {
                "full_name": "Liz Female",
                "given_name": "Liz",
                "family_name": "Female",
                "relationship": BROTHER_SISTER,
                "birth_date": "2005-10-10",  # age 16
                "sex": "FEMALE",
                "registration_data_import": cls.rdi_hub,
                "phone_no": "+41 (0) 78 927 2696",
                "phone_no_alternative": "+41 (0) 78 927 2696",
                "phone_no_valid": None,
                "phone_no_alternative_valid": None,
                "household": imported_household,
                "email": "fake_email_6@com",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "relationship": BROTHER_SISTER,
                "birth_date": "1996-11-29",  # age 25
                "sex": "FEMALE",
                "registration_data_import": cls.rdi_hub,
                "phone_no": "wrong-phone",
                "phone_no_alternative": "definitely-wrong-phone",
                "phone_no_valid": None,
                "phone_no_alternative_valid": None,
                "household": imported_household,
                "email": "fake_email_7@com",
            },
            {
                "full_name": "Bob Jackson",
                "given_name": "Bob",
                "family_name": "Jackson",
                "relationship": BROTHER_SISTER,
                "birth_date": "1956-03-03",  # age 65
                "sex": "MALE",
                "registration_data_import": cls.rdi_hub,
                "household": imported_household,
                "email": "",
            },
        ]

        cls.individuals = [ImportedIndividualFactory(**individual) for individual in individuals_to_create]

    @freeze_time("2022-01-01")
    def test_merge_rdi_and_recalculation(self) -> None:
        imported_household = ImportedHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi_hub,
            admin_area=self.area4.p_code,
            admin_area_title=self.area4.name,
            admin4=self.area4.p_code,
            admin4_title=self.area4.name,
            zip_code="00-123",
            enumerator_rec_id=1234567890,
            detail_id="123456123",
            kobo_asset_id="Test_asset_id",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
        )
        self.set_imported_individuals(imported_household)
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()

        imported_households = ImportedHousehold.objects.all()
        imported_individuals = ImportedIndividual.objects.all()
        household = households.first()

        self.assertEqual(1, households.count())
        self.assertEqual(0, imported_households.count())  # Removed after successful merge
        self.assertEqual(household.collect_individual_data, COLLECT_TYPE_FULL)
        self.assertEqual(8, individuals.count())
        self.assertEqual(0, imported_individuals.count())  # Removed after successful merge
        self.assertEqual(household.flex_fields.get("enumerator_id"), 1234567890)
        self.assertEqual(household.detail_id, "123456123")

        # check KoboImportedSubmission
        kobo_import_submission_qs = KoboImportedSubmission.objects.all()
        kobo_import_submission = kobo_import_submission_qs.first()
        self.assertEqual(kobo_import_submission_qs.count(), 1)
        self.assertEqual(str(kobo_import_submission.kobo_submission_uuid), "c09130af-6c9c-4dba-8c7f-1b2ff1970d19")
        self.assertEqual(kobo_import_submission.kobo_asset_id, "123456123")
        self.assertEqual(str(kobo_import_submission.kobo_submission_time), "2022-02-22 12:22:22+00:00")
        self.assertEqual(kobo_import_submission.imported_household, None)

        individual_with_valid_phone_data = Individual.objects.filter(given_name="Liz").first()
        individual_with_invalid_phone_data = Individual.objects.filter(given_name="Jenna").first()

        self.assertEqual(individual_with_valid_phone_data.phone_no_valid, True)
        self.assertEqual(individual_with_valid_phone_data.phone_no_alternative_valid, True)

        self.assertEqual(individual_with_invalid_phone_data.phone_no_valid, False)
        self.assertEqual(individual_with_invalid_phone_data.phone_no_alternative_valid, False)

        self.assertEqual(Individual.objects.filter(full_name="Baz Bush").first().email, "fake_email_5@com")
        self.assertEqual(Individual.objects.filter(full_name="Benjamin Butler").first().email, "fake_email_1@com")
        self.assertEqual(Individual.objects.filter(full_name="Bob Jackson").first().email, "")
        self.assertEqual(Individual.objects.filter(full_name="Benjamin Butler").first().wallet_name, "Wallet Name 1")
        self.assertEqual(
            Individual.objects.filter(full_name="Benjamin Butler").first().blockchain_name, "Blockchain Name 1"
        )
        self.assertEqual(
            Individual.objects.filter(full_name="Benjamin Butler").first().wallet_address, "Wallet Address 1"
        )

        household_data = model_to_dict(
            household,
            (
                "female_age_group_0_5_count",
                "female_age_group_6_11_count",
                "female_age_group_12_17_count",
                "female_age_group_18_59_count",
                "female_age_group_60_count",
                "male_age_group_0_5_count",
                "male_age_group_6_11_count",
                "male_age_group_12_17_count",
                "male_age_group_18_59_count",
                "male_age_group_60_count",
                "children_count",
                "size",
                "admin_area",
                "admin1",
                "admin2",
                "admin3",
                "admin4",
                "zip_code",
            ),
        )

        expected = {
            "female_age_group_0_5_count": 0,
            "female_age_group_6_11_count": 0,
            "female_age_group_12_17_count": 1,
            "female_age_group_18_59_count": 1,
            "female_age_group_60_count": 0,
            "male_age_group_0_5_count": 1,
            "male_age_group_6_11_count": 1,
            "male_age_group_12_17_count": 2,
            "male_age_group_18_59_count": 1,
            "male_age_group_60_count": 1,
            "children_count": 5,
            "size": 8,
            "admin_area": self.area4.id,
            "admin1": self.area1.id,
            "admin2": self.area2.id,
            "admin3": self.area3.id,
            "admin4": self.area4.id,
            "zip_code": "00-123",
        }
        self.assertEqual(household_data, expected)

    @parameterized.expand(
        [
            True,
            False,
            None,
        ]
    )
    def test_merge_rdi_existing_unicef_id(self, household_collection_exists: bool) -> None:
        imported_household = ImportedHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi_hub,
            admin_area=self.area4.p_code,
            admin_area_title=self.area4.name,
            admin4=self.area4.p_code,
            admin4_title=self.area4.name,
            zip_code="00-123",
            enumerator_rec_id=1234567890,
            detail_id="123456123",
            kobo_asset_id="Test_asset_id",
            kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
            kobo_submission_time="2022-02-22T12:22:22",
            mis_unicef_id="HH-9",
        )
        self.set_imported_individuals(imported_household)
        individual_without_collection = IndividualFactory(
            unicef_id="IND-9",
            business_area=self.rdi.business_area,
            household=None,
        )
        individual_without_collection.individual_collection = None
        individual_without_collection.save()

        individual_collection = IndividualCollectionFactory()
        IndividualFactory(
            unicef_id="IND-8",
            business_area=self.rdi.business_area,
            individual_collection=individual_collection,
            household=None,
        )
        household = None
        household_collection = None
        if household_collection_exists is not None:
            household = HouseholdFactory(
                head_of_household=individual_without_collection,
                business_area=self.rdi.business_area,
                unicef_id="HH-9",
            )
            household.household_collection = None
            household.save()
            if household_collection_exists:
                household_collection = HouseholdCollectionFactory()
                household.household_collection = household_collection
                household.save()

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        individual_without_collection.refresh_from_db()
        self.assertIsNotNone(individual_without_collection.individual_collection)
        self.assertEqual(
            individual_without_collection.individual_collection.individuals.count(),
            2,
        )
        self.assertEqual(
            individual_collection.individuals.count(),
            2,
        )
        if household_collection_exists is not None:
            if household_collection_exists:
                household_collection.refresh_from_db()
                self.assertEqual(household_collection.households.count(), 2)
            else:
                household.refresh_from_db()
                self.assertIsNotNone(household.household_collection)
                self.assertEqual(household.household_collection.households.count(), 2)

    @freeze_time("2022-01-01")
    def test_merge_rdi_and_recalculation_for_collect_data_partial(self) -> None:
        imported_household = ImportedHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_PARTIAL,
            registration_data_import=self.rdi_hub,
        )
        self.set_imported_individuals(imported_household)

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        households = Household.objects.all()
        individuals = Individual.objects.all()

        self.assertEqual(1, households.count())
        self.assertEqual(households[0].collect_individual_data, COLLECT_TYPE_PARTIAL)
        self.assertEqual(8, individuals.count())

        household_data = model_to_dict(
            households[0],
            (
                "female_age_group_0_5_count",
                "female_age_group_6_11_count",
                "female_age_group_12_17_count",
                "female_age_group_18_59_count",
                "female_age_group_60_count",
                "male_age_group_0_5_count",
                "male_age_group_6_11_count",
                "male_age_group_12_17_count",
                "male_age_group_18_59_count",
                "male_age_group_60_count",
                "children_count",
                "size",
            ),
        )

        expected = {
            "female_age_group_0_5_count": None,
            "female_age_group_6_11_count": None,
            "female_age_group_12_17_count": None,
            "female_age_group_18_59_count": None,
            "female_age_group_60_count": None,
            "male_age_group_0_5_count": None,
            "male_age_group_6_11_count": None,
            "male_age_group_12_17_count": None,
            "male_age_group_18_59_count": None,
            "male_age_group_60_count": None,
            "children_count": None,
            "size": None,
        }
        self.assertEqual(household_data, expected)

    @pytest.mark.skip("Bad migrations to fix")
    def test_registration_id_from_program_registration_id_should_be_unique(self) -> None:
        imported_household = ImportedHouseholdFactory(
            registration_data_import=self.rdi_hub,
            program_registration_id="ABCD-123123",
        )
        self.set_imported_individuals(imported_household)
        imported_household = ImportedHouseholdFactory(
            registration_data_import=self.rdi_hub,
            program_registration_id="ABCD-123123",
        )
        self.set_imported_individuals(imported_household)
        imported_household = ImportedHouseholdFactory(
            registration_data_import=self.rdi_hub,
            program_registration_id="ABCD-111111",
        )
        self.set_imported_individuals(imported_household)

        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)

        registrations_ids = list(
            Household.objects.all().order_by("registration_id").values_list("registration_id", flat=True)
        )

        expected_registrations_ids = ["ABCD-111111#0", "ABCD-123123#0", "ABCD-123123#1"]
        self.assertEqual(registrations_ids, expected_registrations_ids)

    def test_merging_external_collector(self) -> None:
        imported_household = ImportedHouseholdFactory(
            collect_individual_data=COLLECT_TYPE_FULL,
            registration_data_import=self.rdi_hub,
            admin_area=self.area4.p_code,
            admin_area_title=self.area4.name,
            admin4=self.area4.p_code,
            admin4_title=self.area4.name,
            zip_code="00-123",
            enumerator_rec_id=1234567890,
        )
        self.set_imported_individuals(imported_household)
        external_collector = ImportedIndividualFactory(
            **{
                "full_name": "External Collector",
                "given_name": "External",
                "family_name": "Collector",
                "relationship": NON_BENEFICIARY,
                "birth_date": "1962-02-02",  # age 39
                "sex": "MALE",
                "registration_data_import": self.rdi_hub,
                "email": "xd@com",
            }
        )
        role = ImportedIndividualRoleInHousehold(
            individual=external_collector, household=imported_household, role=ROLE_ALTERNATE
        )
        role.save()
        with capture_on_commit_callbacks(execute=True):
            RdiMergeTask().execute(self.rdi.pk)
