from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaFactory, AdminAreaTypeFactory
from core.models import BusinessArea
from program.fixtures import ProgramFactory


class TestChangeProgramStatus(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          status
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()

        business_area = BusinessArea.objects.first()
        state_area_type = AdminAreaTypeFactory(name="State", business_area=business_area, admin_level=1)
        self.admin_area = AdminAreaFactory(admin_area_type=state_area_type)

    def test_draft_to_active(self):
        program = ProgramFactory.create(status="DRAFT", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "ACTIVE"}},
        )

    def test_active_to_finished(self):
        program = ProgramFactory.create(status="ACTIVE", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "FINISHED"}},
        )

    def test_finished_to_active(self):
        program = ProgramFactory.create(status="FINISHED", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "ACTIVE"}},
        )

    def test_draft_to_finished(self):
        program = ProgramFactory.create(status="DRAFT", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "FINISHED"}},
        )

    def test_active_to_draft(self):
        program = ProgramFactory.create(status="ACTIVE", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "DRAFT"}},
        )

    def test_finished_to_draft(self):
        program = ProgramFactory.create(status="FINISHED", business_area=BusinessArea.objects.order_by("?").first(),)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={"programData": {"id": self.id_to_base64(program.id, "ProgramNode"), "status": "DRAFT"}},
        )
