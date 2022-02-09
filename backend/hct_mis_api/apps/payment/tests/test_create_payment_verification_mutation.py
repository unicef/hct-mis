from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import CashPlanFactory


class TestCreatePaymentVerificationMutation(APITestCase):
    MUTATION = """
        mutation createCashPlanPaymentVerification( $input: CreatePaymentVerificationInput! ) {
            createCashPlanPaymentVerification(input: $input) {
                cashPlan {
                    id
                }
            }
        }
    """

    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        call_command("loadbusinessareas")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")

        self.cash_plan = CashPlanFactory.create(
            id="0e2927af-c84d-4852-bb0b-773efe059e05",
            business_area=self.business_area,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PAYMENT_VERIFICATION_CREATE]),
            ("without_permission", []),
        ]
    )
    def test_create_cash_plan_payment_verification(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "cashPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
                    "sampling": "FULL_LIST",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "randomSamplingArguments": None,
                    "businessAreaSlug": "afghanistan",
                }
            },
        )

    def test_create_cash_plan_payment_verification_when_invalid_arguments(self):
        self.create_user_role_with_permissions(self.user, [Permissions.PAYMENT_VERIFICATION_CREATE], self.business_area)

        defaults = {
            "cashPlanId": self.id_to_base64(self.cash_plan.id, "CashPlanNode"),
            "businessAreaSlug": "afghanistan",
        }

        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **defaults,
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "sampling": "FULL_LIST",
                    "fullListArguments": None,
                    "randomSamplingArguments": {
                        "confidenceInterval": 1.0,
                        "marginOfError": 1.1,
                    },
                }
            },
        )
        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **defaults,
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": None,
                    "sampling": "RANDOM",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "randomSamplingArguments": None,
                }
            },
        )
        self.snapshot_graphql_request(
            request_string=self.MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **defaults,
                    "sampling": "RANDOM",
                    "fullListArguments": {"excludedAdminAreas": []},
                    "randomSamplingArguments": {
                        "confidenceInterval": 1.0,
                        "marginOfError": 1.1,
                    },
                    "verificationChannel": "MANUAL",
                    "rapidProArguments": {
                        "flowId": 123,
                    },
                }
            },
        )
