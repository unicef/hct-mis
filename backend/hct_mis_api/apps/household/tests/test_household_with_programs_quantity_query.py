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
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
)
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import ProgramFactory


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
        program1 = ProgramFactory.create(name="Test program ONE", business_area=cls.business_area)
        program2 = ProgramFactory.create(name="Test program TWO", business_area=cls.business_area)
        program3 = ProgramFactory.create(name="Test program THREE", business_area=cls.business_area)

        cash_plans_program1 = CashPlanFactory.create_batch(2, program=program1)
        cash_plans_program2 = CashPlanFactory.create_batch(2, program=program2)

        PaymentRecordFactory.create_batch(
            3,
            parent=cash_plans_program1[0],
            currency="AFG",
            delivered_quantity_usd=50,
            delivered_quantity=100,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )
        PaymentRecordFactory.create_batch(
            3,
            parent=cash_plans_program1[1],
            currency="AFG",
            delivered_quantity_usd=100,
            delivered_quantity=150,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )

        PaymentRecordFactory.create_batch(
            3,
            parent=cash_plans_program2[0],
            currency="AFG",
            delivered_quantity_usd=100,
            delivered_quantity=200,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )
        PaymentRecordFactory.create_batch(
            3,
            parent=cash_plans_program2[1],
            currency="AFG",
            delivered_quantity_usd=150,
            delivered_quantity=200,
            household=household,
            status=PaymentRecord.STATUS_SUCCESS,
        )

        cls.household.programs.add(program1)
        cls.household.programs.add(program2)

        payment_plan_program1 = PaymentPlanFactory(program=program1)
        payment_plan_program2 = PaymentPlanFactory(program=program2)
        payment_plan_program3 = PaymentPlanFactory(program=program3)

        PaymentFactory(
            parent=payment_plan_program1,
            currency="AFG",
            delivered_quantity_usd=33,
            delivered_quantity=133,
            household=cls.household,
        )
        PaymentFactory(
            parent=payment_plan_program2,
            currency="AFG",
            delivered_quantity_usd=22,
            delivered_quantity=122,
            household=cls.household,
        )
        PaymentFactory(
            parent=payment_plan_program3,
            currency="AFG",
            delivered_quantity_usd=66,
            delivered_quantity=166,
            household=cls.household,
        )

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
