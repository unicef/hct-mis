import uuid
from typing import Dict
from unittest.mock import MagicMock, patch

from django.test import TestCase

import requests

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanPaymentVerificationFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
)
from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentVerification,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.program.fixtures import CashPlanFactory, ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestPhoneNumberVerification(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.payment_record_amount = 110
        user = UserFactory()

        ###

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan = CashPlanFactory(
            program=program,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan.save()
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            status=CashPlanPaymentVerification.STATUS_PENDING,
            verification_channel=CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO,
            cash_plan=cash_plan,
        )
        cls.individuals = []
        for i in range(cls.payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {
                    "registration_data_import": registration_data_import,
                    "phone_no": f"+48 609 999 {i:03d}",
                },
            )
            cls.individuals.append(individuals[0])

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                cash_plan=cash_plan,
                household=household,
                head_of_household=household.head_of_household,
                target_population=target_population,
                delivered_quantity_usd=200,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verifications.first()

        ###

        other_program = ProgramFactory(business_area=BusinessArea.objects.first())
        other_program.admin_areas.set(Area.objects.order_by("?")[:3])
        other_targeting_criteria = TargetingCriteriaFactory()

        other_target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=other_targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        other_cash_plan = CashPlanFactory(
            program=program,
            business_area=BusinessArea.objects.first(),
        )
        other_cash_plan.save()
        other_cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            status=CashPlanPaymentVerification.STATUS_PENDING,
            verification_channel=CashPlanPaymentVerification.VERIFICATION_CHANNEL_RAPIDPRO,
            cash_plan=other_cash_plan,
        )
        cls.other_individuals = []
        for _ in range(cls.payment_record_amount):
            other_registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            other_household, other_individuals = create_household(
                {
                    "registration_data_import": other_registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": other_registration_data_import},
            )
            cls.other_individuals.append(other_individuals[0])

            other_household.programs.add(program)

            other_payment_record = PaymentRecordFactory(
                cash_plan=other_cash_plan,
                household=other_household,
                head_of_household=other_household.head_of_household,
                target_population=other_target_population,
                delivered_quantity_usd=200,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=other_cash_plan_payment_verification,
                payment_record=other_payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=other_household)
        cls.other_cash_plan = other_cash_plan
        cls.other_verification = other_cash_plan.verifications.first()

    def test_failing_rapid_pro_during_cash_plan_payment_verification(self):
        self.assertEqual(self.verification.status, PaymentVerification.STATUS_PENDING)
        self.assertIsNone(self.verification.error)
        self.assertEqual(self.verification.payment_record_verifications.count(), self.payment_record_amount)

        def create_flow_response() -> Dict:
            return {
                "uuid": str(uuid.uuid4()),
            }

        first_flow = create_flow_response()

        post_request_mock = MagicMock()
        post_request_mock.side_effect = [first_flow, requests.exceptions.HTTPError("TEST")]
        with patch(
            "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)
        ), patch("hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI._handle_post_request", post_request_mock):
            try:
                VerificationPlanStatusChangeServices(self.verification).activate()
            except requests.exceptions.HTTPError:
                pass
            else:
                self.fail("Should have raised HTTPError")

        self.verification.refresh_from_db()
        self.assertEqual(self.verification.status, CashPlanPaymentVerification.STATUS_RAPID_PRO_ERROR)
        self.assertIsNotNone(self.verification.error)

        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            100,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            10,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            self.payment_record_amount,
        )

        post_request_mock = MagicMock()
        post_request_mock.side_effect = [first_flow, create_flow_response()]
        with patch(
            "hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI.__init__", MagicMock(return_value=None)
        ), patch("hct_mis_api.apps.payment.services.rapid_pro.api.RapidProAPI._handle_post_request", post_request_mock):
            VerificationPlanStatusChangeServices(self.verification).activate()

        self.verification.refresh_from_db()
        self.assertEqual(self.verification.status, CashPlanPaymentVerification.STATUS_ACTIVE)
        self.assertIsNone(self.verification.error)

        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification, status=PaymentVerification.STATUS_PENDING
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            self.payment_record_amount,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=True,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            0,
        )
        self.assertEqual(
            PaymentVerification.objects.filter(
                cash_plan_payment_verification=self.other_verification,
                status=PaymentVerification.STATUS_PENDING,
                sent_to_rapid_pro=False,
            ).count(),
            self.payment_record_amount,
        )
