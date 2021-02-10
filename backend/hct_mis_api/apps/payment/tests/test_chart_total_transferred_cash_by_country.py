from datetime import datetime
from django.core.management import call_command
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import CashPlanFactory


class TestChartTotalTransferredCashByCountry(APITestCase):
    CHART_TOTAL_TRANSFERRED_CASH_BY_COUNTRY_QUERY = """
    query ChartTotalTransferredCashByCountry($year: Int!) {
      chartTotalTransferredCashByCountry(year: $year) {
        datasets {
          data
          label
        }
        labels
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        (household, _) = create_household(household_args={"size": 1})
        cash_plan = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        chosen_business_areas = ("afghanistan", "botswana", "angola")
        for business_area_slug in chosen_business_areas:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            PaymentRecordFactory.create_batch(
                3,
                created_at=datetime(year=2021, day=1, month=1),
                business_area=business_area,
                delivery_type=PaymentRecord.DELIVERY_TYPE_CASH,
                status=PaymentRecord.STATUS_SUCCESS,
                entitlement_quantity=200.20,
                delivered_quantity_usd=200.20,
                cash_plan=cash_plan,
                household=household,
            )
            PaymentRecordFactory.create_batch(
                3,
                created_at=datetime(year=2021, day=1, month=1),
                business_area=business_area,
                delivery_type=PaymentRecord.DELIVERY_TYPE_CASH,
                status=PaymentRecord.STATUS_PENDING,
                entitlement_quantity=100.10,
                delivered_quantity_usd=0,
                cash_plan=cash_plan,
                household=household,
            )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.DASHBOARD_VIEW_HQ],
            ),
            ("without_permission", []),
        ]
    )
    def test_resolving_chart(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, BusinessArea.objects.get(slug="global"))

        self.snapshot_graphql_request(
            request_string=self.CHART_TOTAL_TRANSFERRED_CASH_BY_COUNTRY_QUERY,
            context={"user": self.user},
            variables={"year": 2021},
        )
