from datetime import date

from django.core.management import call_command
from django_countries.fields import Country

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
)
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory, DocumentFactory
from household.models import (
    SINGLE,
    Individual,
    ROLE_PRIMARY,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Document, DocumentType, IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
)
from program.fixtures import ProgramFactory


class TestCloseDataChangeTickets(APITestCase):
    STATUS_CHANGE_MUTATION = """
    mutation GrievanceStatusChange($grievanceTicketId: ID!, $status: Int) {
      grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            individualData
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.generate_document_types_for_all_countries()
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area, )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first(), )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in self.individuals_to_create
        ]
        first_individual = self.individuals[0]
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=first_individual
        )
        self.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=first_individual
        )
        household_one.head_of_household = self.individuals[0]
        household_one.save()
        self.household_one = household_one

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketAddIndividualDetailsFactory(
            ticket=self.add_individual_grievance_ticket,
            household=self.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "role": ROLE_PRIMARY,
                "documents": [
                    {"type": IDENTIFICATION_TYPE_NATIONAL_ID, "country": "POL", "number": "123-123-UX-321"}],
            },
            approve_status=True,
        )

        self.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test", "approve_status": True},
                "full_name": {"value": "Test Example", "approve_status": True},
                "family_name": {"value": "Example", "approve_status": True},
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": True},
                "role": {"value": ROLE_PRIMARY, "approve_status": True},
                "documents": [
                    {
                        "value": {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "999-888-777"},
                        "approve_status": True,
                    },
                ],
                "documents_to_remove": [
                    {"value": self.id_to_base64(self.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": self.id_to_base64(self.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
            },
        )

        self.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={
                "village": {"value": "Test Village", "approve_status": True},
                "size": {"value": 19, "approve_status": True},
            },
        )

    def test_close_add_individual(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        created_individual = Individual.objects.filter(
            given_name="Test", full_name="Test Example", family_name="Example", sex="MALE",
        )
        self.assertTrue(created_individual.exists())

        created_individual = created_individual.first()

        document = Document.objects.get(document_number="123-123-UX-321")
        self.assertEqual(document.type.country, Country("POL"))

        role = created_individual.households_and_roles.get(role=ROLE_PRIMARY, individual=created_individual)
        self.assertEqual(str(role.household.id), str(self.household_one.id))

    def test_close_update_individual(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        self.assertEqual(individual.given_name, "Test")
        self.assertEqual(individual.full_name, "Test Example")
        self.assertEqual(individual.family_name, "Example")
        self.assertEqual(individual.marital_status, SINGLE)
        self.assertNotEqual(individual.birth_date, date(year=1980, month=2, day=1))

        role = individual.households_and_roles.get(role=ROLE_PRIMARY, individual=individual)
        self.assertEqual(str(role.household.id), str(self.household_one.id))

        document = Document.objects.get(document_number="999-888-777")
        self.assertEqual(document.type.country, Country("POL"))
        self.assertEqual(document.type.type, IDENTIFICATION_TYPE_NATIONAL_ID)

        self.assertFalse(Document.objects.filter(id=self.national_id.id).exists())
        self.assertTrue(Document.objects.filter(id=self.birth_certificate.id).exists())

    def test_close_update_household(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.household_one.refresh_from_db()
        self.assertEqual(self.household_one.size, 19)
        self.assertEqual(self.household_one.village, "Test Village")
