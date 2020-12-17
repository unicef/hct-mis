from django.core.management import call_command
from parameterized import parameterized

from account.fixtures import UserFactory
from account.permissions import Permissions
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import create_household
from program.fixtures import ProgramFactory
from program.models import Program


class TestCreateTargetPopulationMutation(APITestCase):
    MUTATION_QUERY = """
    mutation CreateTargetPopulation($createTargetPopulationInput: CreateTargetPopulationInput!) {
      createTargetPopulation(input: $createTargetPopulationInput) {
        targetPopulation{
          name
          status
          candidateListTotalHouseholds
          candidateListTotalIndividuals
            candidateListTargetingCriteria{
            rules{
              filters{
                comparisionMethod
                fieldName
                arguments
                isFlexField
              }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        call_command("loadbusinessareas")
        create_household(
            {"size": 2, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        create_household(
            {"size": 3, "residence_status": "HOST"},
        )
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(status=Program.ACTIVE, business_area=business_area)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.TARGETING_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_mutation(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.program.business_area)

        variables = {
            "createTargetPopulationInput": {
                "name": "Example name 5",
                "businessAreaSlug": "afghanistan",
                "programId": self.id_to_base64(self.program.id, "ProgramNode"),
                "targetingCriteria": {
                    "rules": [
                        {
                            "filters": [
                                {
                                    "comparisionMethod": "EQUALS",
                                    "fieldName": "size",
                                    "arguments": [3],
                                    "isFlexField": False,
                                }
                            ]
                        }
                    ]
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=TestCreateTargetPopulationMutation.MUTATION_QUERY,
            context={"user": self.user},
            variables=variables,
        )
