import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    FspXlsxTemplatePerDeliveryMechanism,
    PaymentPlan,
    PaymentPlanSplit,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.payment.utils import to_decimal
from hct_mis_api.apps.payment.xlsx.xlsx_error import XlsxError
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
    XlsxPaymentPlanExportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_service import (
    XlsxPaymentPlanExportService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_import_service import (
    XlsxPaymentPlanImportService,
)


def valid_file() -> File:
    content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/pp_payment_list_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_valid.xlsx")


def invalid_file() -> File:
    content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/pp_payment_list_invalid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_invalid.xlsx")


class ImportExportPaymentPlanPaymentListTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        if not Household.objects.all().count():
            for n in range(1, 4):
                create_household(
                    {"size": n, "address": "Lorem Ipsum", "country_origin": country_origin},
                )

        if ServiceProvider.objects.count() < 3:
            ServiceProviderFactory.create_batch(3)
        program = RealProgramFactory()
        cls.payment_plan = PaymentPlanFactory(program=program, business_area=cls.business_area)
        fsp_1 = FinancialServiceProviderFactory(
            name="Test FSP 1",
            delivery_mechanisms=[DeliveryMechanismChoices.DELIVERY_TYPE_CASH],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            vision_vendor_number=123456789,
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=fsp_1, delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan,
            financial_service_provider=fsp_1,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH,
            delivery_mechanism_order=1,
        )
        program.households.set(Household.objects.all().values_list("id", flat=True))
        for household in program.households.all():
            PaymentFactory(
                parent=cls.payment_plan, household=household, financial_service_provider=fsp_1, currency="PLN"
            )

        cls.user = UserFactory()
        cls.payment_plan = PaymentPlan.objects.all()[0]

        # set Lock status
        cls.payment_plan.status_lock()
        cls.payment_plan.save()

        cls.xlsx_valid_file = FileTemp.objects.create(
            object_id=cls.payment_plan.pk,
            content_type=get_content_type_for_model(cls.payment_plan),
            created_by=cls.user,
            file=valid_file(),
        ).file

        cls.xlsx_invalid_file = FileTemp.objects.create(
            object_id=cls.payment_plan.pk,
            content_type=get_content_type_for_model(cls.payment_plan),
            created_by=cls.user,
            file=invalid_file(),
        ).file

    def test_import_invalid_file(self) -> None:
        error_msg = [
            XlsxError(
                "Payment Plan - Payment List", "A2", "This payment id 123123 is not in Payment Plan Payment List"
            ),
        ]
        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_invalid_file)
        wb = service.open_workbook()
        # override imported sheet payment id
        wb.active["A3"].value = str(self.payment_plan.eligible_payments[1].unicef_id)

        service.validate()
        self.assertEqual(service.errors, error_msg)

    def test_import_invalid_file_with_unexpected_column(self) -> None:
        error_msg = XlsxError(sheet="Payment Plan - Payment List", coordinates="L3", message="Unexpected value")
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/pp_payment_list_unexpected_column.xlsx"
        ).read_bytes()
        file = BytesIO(content)

        service = XlsxPaymentPlanImportService(self.payment_plan, file)
        service.open_workbook()
        service.validate()
        self.assertIn(error_msg, service.errors)

    @patch("hct_mis_api.apps.core.exchange_rates.api.ExchangeRateClientAPI.__init__")
    def test_import_valid_file(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        not_excluded_payments = self.payment_plan.eligible_payments.all()
        # override imported payment id
        payment_id_1 = str(not_excluded_payments[0].unicef_id)
        payment_id_2 = str(not_excluded_payments[1].unicef_id)
        payment_1 = not_excluded_payments[0]
        payment_2 = not_excluded_payments[1]

        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_valid_file)
        wb = service.open_workbook()

        wb.active["A2"].value = payment_id_1
        wb.active["A3"].value = payment_id_2

        service.validate()
        self.assertEqual(service.errors, [])

        with patch("hct_mis_api.apps.core.exchange_rates.api.ExchangeRateClientAPI.fetch_exchange_rates") as mock:
            mock.return_value = {}
            service.import_payment_list()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(to_decimal(wb.active["I2"].value), payment_1.entitlement_quantity)
        self.assertEqual(to_decimal(wb.active["I3"].value), payment_2.entitlement_quantity)

    def test_export_payment_plan_payment_list(self) -> None:
        export_service = XlsxPaymentPlanExportService(self.payment_plan)
        export_service.save_xlsx_file(self.user)

        self.assertTrue(self.payment_plan.has_export_file)

        wb = export_service.generate_workbook()
        payment = self.payment_plan.eligible_payments.order_by("unicef_id").first()
        self.assertEqual(wb.active["A2"].value, str(payment.unicef_id))
        self.assertEqual(wb.active["I2"].value, payment.entitlement_quantity)
        self.assertEqual(wb.active["J2"].value, payment.entitlement_quantity_usd)
        self.assertEqual(wb.active["D2"].value, "")

    def test_export_payment_plan_payment_list_per_fsp(self) -> None:
        financial_service_provider1 = FinancialServiceProviderFactory(
            delivery_mechanisms=[DeliveryMechanismChoices.DELIVERY_TYPE_CASH]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider1,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH,
        )
        financial_service_provider2 = FinancialServiceProviderFactory(
            delivery_mechanisms=[DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider2,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER,
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH,
            financial_service_provider=financial_service_provider1,
            delivery_mechanism_order=2,
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_TRANSFER,
            financial_service_provider=financial_service_provider2,
            delivery_mechanism_order=3,
        )
        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()

        payment = self.payment_plan.eligible_payments.first()
        self.assertEqual(payment.token_number, None)
        self.assertEqual(payment.order_number, None)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        payment.refresh_from_db(fields=["token_number", "order_number"])
        self.assertEqual(len(str(payment.token_number)), 7)
        self.assertEqual(len(str(payment.order_number)), 9)

        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        fsp_ids = self.payment_plan.delivery_mechanisms.values_list("financial_service_provider_id", flat=True)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:
            file_list = zip_file.namelist()
            self.assertEqual(len(fsp_ids), len(file_list))
            fsp_xlsx_template_per_delivery_mechanism_list = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id__in=fsp_ids,
            )
            file_list_fsp = [
                f.replace(".xlsx", "").replace(f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_", "")
                for f in file_list
            ]
            for fsp_xlsx_template_per_delivery_mechanism in fsp_xlsx_template_per_delivery_mechanism_list:
                self.assertIn(
                    f"{fsp_xlsx_template_per_delivery_mechanism.financial_service_provider.name}_{fsp_xlsx_template_per_delivery_mechanism.delivery_mechanism}",
                    file_list_fsp,
                )

    @patch("hct_mis_api.apps.payment.models.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
    def test_export_payment_plan_payment_list_per_split(self, min_no_of_payments_in_chunk_mock: Any) -> None:
        min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

        financial_service_provider1 = FinancialServiceProviderFactory(
            delivery_mechanisms=[DeliveryMechanismChoices.DELIVERY_TYPE_CASH]
        )
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider1,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH,
            financial_service_provider=financial_service_provider1,
            delivery_mechanism_order=2,
        )

        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()

        payments = self.payment_plan.eligible_payments.all()
        self.assertEqual(payments.count(), 3)

        pp_service = PaymentPlanService(self.payment_plan)
        pp_service.split(PaymentPlanSplit.SplitType.BY_RECORDS, 2)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        splits_count = self.payment_plan.splits.count()
        self.assertEqual(splits_count, 2)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:
            file_list = zip_file.namelist()
            self.assertEqual(splits_count, len(file_list))

        # reexport
        pp_service.split(PaymentPlanSplit.SplitType.BY_COLLECTOR)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)
        self.payment_plan.refresh_from_db()
        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        splits_count = self.payment_plan.splits.count()
        self.assertEqual(splits_count, 3)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:
            file_list = zip_file.namelist()
            self.assertEqual(splits_count, len(file_list))
