from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory


class TestHouseholdWithProgramsQuantityQuery(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    QUERY = """
        query Household($id: ID!) {
          household(id: $id) {
            programsWithDeliveredQuantity {
              name
              quantity {
                totalDeliveredQuantity
                currency
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        household, _ = create_household(
            {
                "size": 2,
                "address": "Lorem Ipsum",
                "country_origin": geo_models.Country.objects.filter(iso_code2="PL").first(),
            }
        )
        cls.household = household
        cls.program1 = ProgramFactory.create(name="Test program ONE", business_area=cls.business_area)
        cls.program2 = ProgramFactory.create(name="Test program TWO", business_area=cls.business_area)

        cash_plans_program1 = CashPlanFactory.create_batch(2, program=cls.program1)
        cash_plans_program2 = CashPlanFactory.create_batch(2, program=cls.program2)

        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plans_program1[0],
            currency="AFG",
            delivered_quantity_usd=50,
            delivered_quantity=100,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )
        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plans_program1[1],
            currency="AFG",
            delivered_quantity_usd=100,
            delivered_quantity=200,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )

        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plans_program2[0],
            currency="USD",
            delivered_quantity_usd=100,
            delivered_quantity=100,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )
        PaymentRecordFactory.create_batch(
            3,
            cash_plan=cash_plans_program2[1],
            currency="USD",
            delivered_quantity_usd=200,
            delivered_quantity=200,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )

        cls.household.programs.add(cls.program1)
        cls.household.programs.add(cls.program2)

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_household_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.household.id, "HouseholdNode")},
        )
