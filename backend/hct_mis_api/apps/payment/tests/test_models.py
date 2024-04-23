import json
from datetime import datetime
from typing import Any
from unittest.mock import patch

from django.db.utils import IntegrityError
from django.test import TestCase

from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.currencies import USDC
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
    RealProgramFactory,
)
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)


class TestPaymentPlanModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self) -> None:
        pp = PaymentPlanFactory()
        self.assertIsInstance(pp, PaymentPlan)

    def test_update_population_count_fields(self) -> None:
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        PaymentFactory(parent=pp, household=hh1, head_of_household=hoh1, currency="PLN")
        PaymentFactory(parent=pp, household=hh2, head_of_household=hoh2, currency="PLN")

        IndividualFactory(household=hh1, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=5))
        IndividualFactory(household=hh1, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=5))
        IndividualFactory(household=hh2, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=20))
        IndividualFactory(household=hh2, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=20))

        pp.update_population_count_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.female_children_count, 1)
        self.assertEqual(pp.male_children_count, 1)
        self.assertEqual(pp.female_adults_count, 1)
        self.assertEqual(pp.male_adults_count, 1)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_money_fields(self, get_exchange_rate_mock: Any) -> None:
        pp = PaymentPlanFactory()
        PaymentFactory(
            parent=pp,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
        )
        PaymentFactory(
            parent=pp,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
        )

        pp.update_money_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.exchange_rate, 2.0)
        self.assertEqual(pp.total_entitled_quantity, 200.00)
        self.assertEqual(pp.total_entitled_quantity_usd, 400.00)
        self.assertEqual(pp.total_delivered_quantity, 100.00)
        self.assertEqual(pp.total_delivered_quantity_usd, 200.00)
        self.assertEqual(pp.total_undelivered_quantity, 100.00)
        self.assertEqual(pp.total_undelivered_quantity_usd, 200.00)

    def test_not_excluded_payments(self) -> None:
        pp = PaymentPlanFactory()
        PaymentFactory(parent=pp, conflicted=False, currency="PLN")
        PaymentFactory(parent=pp, conflicted=True, currency="PLN")

        pp.refresh_from_db()
        self.assertEqual(pp.eligible_payments.count(), 1)

    def test_can_be_locked(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program=program, program_cycle=program_cycle)
        self.assertEqual(pp1.can_be_locked, False)

        # create hard conflicted payment
        pp1_conflicted = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.LOCKED,
            program=program,
            program_cycle=program_cycle,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        PaymentFactory(parent=pp1_conflicted, household=p1.household, conflicted=False, currency="PLN")
        self.assertEqual(pp1.payment_items.filter(payment_plan_hard_conflicted=True).count(), 1)
        self.assertEqual(pp1.can_be_locked, False)

        # create not conflicted payment
        PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        self.assertEqual(pp1.can_be_locked, True)

    def test_get_exchange_rate_for_usdc_currency(self) -> None:
        pp = PaymentPlanFactory(currency=USDC)
        self.assertEqual(pp.get_exchange_rate(), 1.0)


class TestPaymentModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self) -> None:
        p1 = PaymentFactory()
        self.assertIsInstance(p1, Payment)

    def test_unique_together(self) -> None:
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        PaymentFactory(parent=pp, household=hh1, currency="PLN")
        with self.assertRaises(IntegrityError):
            PaymentFactory(parent=pp, household=hh1, currency="PLN")

    def test_manager_annotations__pp_conflicts(self) -> None:
        program = RealProgramFactory()
        program_cycle = program.cycles.first()

        pp1 = PaymentPlanFactory(program=program, program_cycle=program_cycle)

        # create hard conflicted payment
        pp2 = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.LOCKED,
            program=program,
            program_cycle=program_cycle,
        )
        # create soft conflicted payments
        pp3 = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.OPEN,
            program=program,
            program_cycle=program_cycle,
        )
        pp4 = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.OPEN,
            program=program,
            program_cycle=program_cycle,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        p2 = PaymentFactory(parent=pp2, household=p1.household, conflicted=False, currency="PLN")
        p3 = PaymentFactory(parent=pp3, household=p1.household, conflicted=False, currency="PLN")
        p4 = PaymentFactory(parent=pp4, household=p1.household, conflicted=False, currency="PLN")

        for _ in [pp1, pp2, pp3, pp4, p1, p2, p3, p4]:
            _.refresh_from_db()  # update unicef_id from trigger

        p1_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(p1_data["payment_plan_hard_conflicted"], True)
        self.assertEqual(p1_data["payment_plan_soft_conflicted"], True)

        self.assertEqual(len(p1_data["payment_plan_hard_conflicted_data"]), 1)
        self.assertEqual(
            json.loads(p1_data["payment_plan_hard_conflicted_data"][0]),
            {
                "payment_id": str(p2.id),
                "payment_plan_id": str(pp2.id),
                "payment_plan_status": str(pp2.status),
                "payment_plan_start_date": pp2.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": pp2.end_date.strftime("%Y-%m-%d"),
                "payment_plan_unicef_id": str(pp2.unicef_id),
                "payment_unicef_id": str(p2.unicef_id),
            },
        )
        self.assertEqual(len(p1_data["payment_plan_soft_conflicted_data"]), 2)
        self.assertCountEqual(
            [json.loads(conflict_data) for conflict_data in p1_data["payment_plan_soft_conflicted_data"]],
            [
                {
                    "payment_id": str(p3.id),
                    "payment_plan_id": str(pp3.id),
                    "payment_plan_status": str(pp3.status),
                    "payment_plan_start_date": pp3.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": pp3.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp3.unicef_id),
                    "payment_unicef_id": str(p3.unicef_id),
                },
                {
                    "payment_id": str(p4.id),
                    "payment_plan_id": str(pp4.id),
                    "payment_plan_status": str(pp4.status),
                    "payment_plan_start_date": pp4.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": pp4.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp4.unicef_id),
                    "payment_unicef_id": str(p4.unicef_id),
                },
            ],
        )

    def test_manager_annotations_pp_no_conflicts_for_follow_up(self) -> None:
        program_cycle = RealProgramFactory().cycles.first()
        pp1 = PaymentPlanFactory(program_cycle=program_cycle)
        # create follow up pp
        pp2 = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.LOCKED,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
        )
        pp3 = PaymentPlanFactory(
            start_date=pp1.start_date,
            end_date=pp1.end_date,
            status=PaymentPlan.Status.OPEN,
            is_follow_up=True,
            source_payment_plan=pp1,
            program_cycle=program_cycle,
        )
        p1 = PaymentFactory(parent=pp1, conflicted=False, currency="PLN")
        p2 = PaymentFactory(
            parent=pp2,
            household=p1.household,
            conflicted=False,
            is_follow_up=True,
            source_payment=p1,
            currency="PLN",
        )
        p3 = PaymentFactory(
            parent=pp3,
            household=p1.household,
            conflicted=False,
            is_follow_up=True,
            source_payment=p1,
            currency="PLN",
        )

        for _ in [pp1, pp2, pp3, p1, p2, p3]:
            _.refresh_from_db()  # update unicef_id from trigger

        p2_data = Payment.objects.filter(id=p2.id).values()[0]
        self.assertEqual(p2_data["payment_plan_hard_conflicted"], False)
        self.assertEqual(p2_data["payment_plan_soft_conflicted"], True)
        p3_data = Payment.objects.filter(id=p3.id).values()[0]
        self.assertEqual(p3_data["payment_plan_hard_conflicted"], False)
        self.assertEqual(p3_data["payment_plan_soft_conflicted"], True)
        self.assertEqual(p2_data["payment_plan_hard_conflicted_data"], [])
        self.assertIsNotNone(p3_data["payment_plan_hard_conflicted_data"])


class TestPaymentPlanSplitModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_properties(self) -> None:
        pp = PaymentPlanFactory()
        dm = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=pp,
            chosen_configuration="key1",
        )
        p1 = PaymentFactory(parent=pp, currency="PLN")
        p2 = PaymentFactory(parent=pp, currency="PLN")
        pp_split1 = PaymentPlanSplitFactory(
            payment_plan=pp,
            split_type=PaymentPlanSplit.SplitType.BY_RECORDS,
            chunks_no=2,
            order=0,
        )
        pp_split1.payments.set([p1, p2])
        self.assertEqual(pp_split1.financial_service_provider, dm.financial_service_provider)
        self.assertEqual(pp_split1.chosen_configuration, dm.chosen_configuration)


class TestFinancialServiceProviderModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_properties(self) -> None:
        fsp1 = FinancialServiceProviderFactory(
            data_transfer_configuration=[
                {"key": "key1", "label": "label1", "id": 1, "random_key": "random"},
                {"key": "key2", "label": "label2", "id": 2, "random_key": "random"},
            ],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id=123,
        )
        fsp2 = FinancialServiceProviderFactory(
            data_transfer_configuration=[
                {"key": "key1", "label": "label1", "id": 1, "random_key": "random"},
                {"key": "key2", "label": "label2", "id": 2, "random_key": "random"},
            ],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        )

        self.assertEqual(
            fsp1.configurations,
            [
                {"key": "key1", "label": "label1", "id": 1},
                {"key": "key2", "label": "label2", "id": 2},
            ],
        )
        self.assertEqual(fsp2.configurations, [])
