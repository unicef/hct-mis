from django.test import TestCase
from rest_framework.test import APIClient

from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.models import ImportedIndividualRoleInHousehold
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedDocumentFactory,
    ImportedDocumentTypeFactory,
    ImportedIndividualFactory,
    ImportedHouseholdFactory,
)
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_TAX_ID, HEAD, ROLE_NO_ROLE
from hct_mis_api.apps.household.fixtures import DocumentFactory, DocumentTypeFactory, create_household


class TestDetails(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.api_client = APIClient()
        cls.api_client.force_authenticate(user=cls.user)

        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )

    def test_getting_non_existent_individual(self):
        response = self.api_client.get("/api/details?tax_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    def test_getting_individual_with_status_imported(self):
        imported_household = ImportedHouseholdFactory()
        imported_individual = ImportedIndividualFactory(household=imported_household, relationship=HEAD)
        imported_household.head_of_household = imported_individual
        imported_household.save()
        ImportedIndividualRoleInHousehold.objects.create(
            individual=imported_individual, role=ROLE_NO_ROLE, household=imported_household
        )

        imported_document_type = ImportedDocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        imported_document = ImportedDocumentFactory(individual=imported_individual, type=imported_document_type)
        tax_id = imported_document.document_number

        response = self.api_client.get(f"/api/details?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "imported")
        self.assertEqual(info["date"], str(imported_household.updated_at).replace(" ", "T"))

        individual = info["individual"]
        self.assertIsNotNone(individual)
        self.assertEqual(individual["relationship"], HEAD)
        self.assertEqual(individual["role"], ROLE_NO_ROLE)
        self.assertEqual(individual["tax_id"], tax_id)

    def test_getting_individual_with_status_merged_to_population(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number

        response = self.api_client.get(f"/api/details?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        info = data["info"]
        self.assertEqual(info["status"], "merged to population")
        self.assertEqual(info["date"], str(household.created_at).replace(" ", "T"))

    def test_getting_individual_with_status_targeted(self):
        # TODO: create some objs in db
        # response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        # self.assertEqual(response.status_code, 200)
        # data = response.json()
        # info = data["info"]
        # self.assertEqual(info["status"], "targeted")
        # TODO: date of targeting
        pass

    def test_getting_individual_with_status_sent_to_cash_assist(self):
        # TODO: create some objs in db
        # response = self.api_client.get(f"/api/details?tax_id={self.tax_id}")
        # self.assertEqual(response.status_code, 200)
        # data = response.json()
        # self.assertIsNotNone(data["info"])
        # info = data["info"]
        # self.assertEqual(info["status"], "sent to cash assist")
        # TODO: date of sending to cash assist
        pass

    def test_getting_individual_with_status_paid(self):
        household, individuals = create_household(household_args={"size": 1, "business_area": self.business_area})
        individual = individuals[0]
        document_type = DocumentTypeFactory(type=IDENTIFICATION_TYPE_TAX_ID)
        document = DocumentFactory(individual=individual, type=document_type)
        tax_id = document.document_number
        payment_record = PaymentRecordFactory(household=household)

        response = self.api_client.get(f"/api/details?tax_id={tax_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["info"])
        info = data["info"]
        self.assertEqual(info["status"], "paid")
        self.assertEqual(info["date"], str(payment_record.updated_at).replace(" ", "T"))

    def test_getting_non_existent_household(self):
        response = self.api_client.get("/api/details?registration_id=non-existent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "not found")

    # TODO: test households
    # def test_getting_household(self):
    #     response = self.api_client.get(f"/api/details?registration_id={self.registration_id}")
    #     self.assertEqual(response.status_code, 200)
    #     data = response.json()
    #     self.assertIsNotNone(data["info"])
    #     info = data["info"]
    #     self.assertIsNotNone(info["date"])
    #     self.assertIsNotNone(info["status"])
