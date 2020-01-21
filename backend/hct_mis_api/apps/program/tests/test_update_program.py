from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.base_test_case import APITestCase
from program.fixtures import ProgramFactory
from program.models import Program


class TestUpdateProgram(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          name
          status
        }
      }
    }
    """

    def test_update_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": "UHJvZ3JhbU5vZGU6MTc4MWEwMGMtMjhl"
                    "OS00OGRmLTlhOTUtZDg5ZWVmYWM1ZmY0",
                    "name": "updated name",
                    "status": "FINISHED",
                }
            },
        )

    def test_update_program_authenticated(self):
        user = UserFactory.create()

        program = ProgramFactory.create(status="DRAFT")

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "name": "updated name",
                    "status": "ACTIVE",
                }
            },
        )

        updated_program = Program.objects.get(id=program.id)

        assert updated_program.status == "ACTIVE"
        assert updated_program.name == "updated name"
