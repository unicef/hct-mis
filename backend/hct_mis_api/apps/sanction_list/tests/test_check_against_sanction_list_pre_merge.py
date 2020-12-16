from constance.test import override_config
from django.conf import settings
from django_countries.fields import Country

from core.base_test_case import BaseElasticSearchTestCase
from core.models import BusinessArea
from household.fixtures import create_household_and_individuals, DocumentFactory
from household.models import Individual, DocumentType, IDENTIFICATION_TYPE_CHOICE, IDENTIFICATION_TYPE_NATIONAL_ID
from registration_data.fixtures import RegistrationDataImportFactory
from sanction_list.tasks.check_against_sanction_list_pre_merge import CheckAgainstSanctionListPreMergeTask
from sanction_list.tasks.load_xml import LoadSanctionListXMLTask


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
class TestSanctionListPreMerge(BaseElasticSearchTestCase):
    multi_db = True

    TEST_FILES_PATH = f"{settings.PROJECT_ROOT}/apps/sanction_list/tests/test_files"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        full_sanction_list_path = f"{cls.TEST_FILES_PATH}/full_sanction_list.xml"
        task = LoadSanctionListXMLTask(full_sanction_list_path)
        task.execute()

        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area,
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={"registration_data_import": cls.registration_data_import},
            individuals_data=[
                {
                    # DUPLICATE
                    "given_name": "Ri",
                    "full_name": "Ri Won Ho",
                    "middle_name": "",
                    "family_name": "Won Ho",
                    "birth_date": "1964-07-17",
                },
                {
                    "given_name": "Choo",
                    "full_name": "Choo Ryoong",
                    "middle_name": "",
                    "family_name": "Ryong",
                    "birth_date": "1960-04-04",
                },
                {
                    "given_name": "Tescik",
                    "full_name": "Tescik Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1996-12-12",
                },
                {
                    # DUPLICATE
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1997-07-07",
                },
                {
                    # DUPLICATE
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1955-09-04",
                },
                {
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "birth_date": "1997-08-08",
                },
                {
                    # DUPLICATE
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1997-07-07",
                },
                {
                    "given_name": "Abdul",
                    "full_name": "Abdul Afghanistan",
                    "middle_name": "",
                    "family_name": "Afghanistan",
                    "birth_date": "1997-07-07",
                },
            ],
        )

        ind = Individual.objects.get(full_name="Abdul Afghanistan")
        doc_type = DocumentType.objects.create(
            country=Country("AFG"),
            label="National ID",
            type=IDENTIFICATION_TYPE_NATIONAL_ID,
        )
        DocumentFactory(document_number="55130", individual=ind, type=doc_type)

        cls.rebuild_search_index()

    def test_execute(self):
        CheckAgainstSanctionListPreMergeTask.execute()

        expected = [
            {"full_name": "Abdul Afghanistan", "sanction_list_possible_match": True},
            {"full_name": "Choo Ryoong", "sanction_list_possible_match": True},
            {"full_name": "Ri Won Ho", "sanction_list_possible_match": True},
            {"full_name": "Tescik Testowski", "sanction_list_possible_match": False},
            {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
            {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
            {"full_name": "Test Example", "sanction_list_possible_match": False},
            {"full_name": "Test Testowski", "sanction_list_possible_match": False},
        ]

        result = list(Individual.objects.order_by("full_name").values("full_name", "sanction_list_possible_match"))

        self.assertEqual(result, expected)
