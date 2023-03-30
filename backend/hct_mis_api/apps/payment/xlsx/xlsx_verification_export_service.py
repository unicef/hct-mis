import logging
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User


logger = logging.getLogger(__name__)


class XlsxVerificationExportService(XlsxExportBaseService):
    HEADERS = (
        "payment_record_id",
        "payment_record_ca_id",
        "received",
        "head_of_household",
        "phone_no",
        "phone_no_alternative",
        "admin1",
        "admin2",
        "village",
        "address",
        "household_id",
        "household_unicef_id",
        "delivered_amount",
        "received_amount",
    )
    PAYMENT_RECORD_ID_COLUMN_INDEX = 0
    PAYMENT_RECORD_ID_LETTER = "A"
    RECEIVED_COLUMN_INDEX = 2
    RECEIVED_COLUMN_LETTER = "C"
    RECEIVED_AMOUNT_COLUMN_INDEX = 13
    RECEIVED_AMOUNT_COLUMN_LETTER = "N"
    VERIFICATION_SHEET = "Payment Verifications"
    META_SHEET = "Meta"
    VERSION_CELL_NAME_COORDINATES = "A1"
    VERSION_CELL_COORDINATES = "B1"
    VERSION_CELL_NAME = "FILE_TEMPLATE_VERSION"
    VERSION = "1.2"
    TRUE_FALSE_MAPPING = {True: "YES", False: "NO"}

    def __init__(self, payment_verification_plan: PaymentVerificationPlan) -> None:
        self.payment_verification_plan = payment_verification_plan
        self.payment_record_verifications = payment_verification_plan.payment_record_verifications.all()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_verifications = wb.active
        ws_verifications.title = XlsxVerificationExportService.VERIFICATION_SHEET
        self.wb = wb
        self.ws_export_list = ws_verifications
        self.ws_meta = wb.create_sheet(XlsxVerificationExportService.META_SHEET)
        return wb

    def _add_version(self) -> None:
        self.ws_meta[
            XlsxVerificationExportService.VERSION_CELL_NAME_COORDINATES
        ] = XlsxVerificationExportService.VERSION_CELL_NAME
        self.ws_meta[XlsxVerificationExportService.VERSION_CELL_COORDINATES] = XlsxVerificationExportService.VERSION

    def _to_received_column(self, payment_record_verification: PaymentVerification) -> Optional[str]:
        status = payment_record_verification.status
        if payment_record_verification.status == PaymentVerification.STATUS_PENDING:
            return None
        if status == PaymentVerification.STATUS_NOT_RECEIVED:
            return XlsxVerificationExportService.TRUE_FALSE_MAPPING[False]
        return XlsxVerificationExportService.TRUE_FALSE_MAPPING[True]

    def _add_payment_record_verification_row(self, payment_record_verification: PaymentVerification) -> None:
        household = payment_record_verification.payment_obj.household
        head_of_household = payment_record_verification.payment_obj.head_of_household

        payment_record_verification_row = (
            str(payment_record_verification.payment_object_id),
            str(payment_record_verification.payment_obj.unicef_id) if payment_record_verification.payment_obj else "",
            self._to_received_column(payment_record_verification),
            str(head_of_household.full_name) if head_of_household else "",
            str(head_of_household.phone_no) if head_of_household else "",
            str(head_of_household.phone_no_alternative) if head_of_household else "",
            str(household.admin1.name) if household.admin1 else "",
            str(household.admin2.name) if household.admin2 else "",
            str(household.village),
            str(household.address),
            str(payment_record_verification.payment_obj.household_id),
            str(household.unicef_id),
            payment_record_verification.payment_obj.delivered_quantity,
            payment_record_verification.received_amount,
        )
        self.ws_export_list.append(payment_record_verification_row)

    def _add_payment_record_verifications(self) -> None:
        for payment_record_verification in self.payment_record_verifications:
            self._add_payment_record_verification_row(payment_record_verification)

    def _add_data_validation(self) -> None:
        self.dv_received = DataValidation(type="list", formula1='"YES,NO"', allow_blank=False)
        self.dv_received.add(f"B2:B{len(self.ws_export_list['B'])}")
        self.ws_export_list.add_data_validation(self.dv_received)
        self.ws_export_list["B2":f"B{len(self.ws_export_list['B'])}"]

    def generate_workbook(self) -> openpyxl.Workbook:
        self._create_workbook()
        self._add_version()
        self._add_headers()
        self._add_payment_record_verifications()
        self._add_data_validation()
        self._adjust_column_width_from_col(self.ws_export_list)  # min_row, min_col, max_col
        return self.wb

    def save_xlsx_file(self, user: "User") -> None:
        filename = f"payment_verification_{self.payment_verification_plan.unicef_id}.xlsx"
        self.generate_workbook()
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.payment_verification_plan.pk,
                content_type=get_content_type_for_model(self.payment_verification_plan),
                created_by=user,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))

    def get_email_context(self, user: "User") -> dict:
        payment_verification_id = encode_id_base64(self.payment_verification_plan.pk, "PaymentVerificationPlan")
        link = self.get_link(reverse("download-payment-verification-plan", args=[payment_verification_id]))

        msg = "Verification Plan xlsx file was generated and below You have the link to download this file."
        context = {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": link,
            "title": "Verification Plan XLSX file generated",
        }

        return context

    def send_email(self, user: "User") -> None:  # type: ignore
        # TODO: this function is not used anywhere yet but once it is, the `user` arg should not override the `context` arg from the base class
        protocol = "http" if settings.IS_DEV else "https"
        payment_verification_id = encode_id_base64(self.payment_verification_plan.id, "PaymentVerificationPlan")
        api = reverse("download-payment-verification-plan", args=[payment_verification_id])
        link = f"{protocol}://{settings.FRONTEND_HOST}{api}"

        msg = "Verification Plan xlsx file was generated and below You have the link to download this file."
        context = {
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "email": getattr(user, "email", ""),
            "message": msg,
            "link": link,
        }
        text_body = render_to_string("payment/verification_plan_xlsx_file_generated_email.txt", context=context)
        html_body = render_to_string("payment/verification_plan_xlsx_file_generated_email.html", context=context)

        email = EmailMultiAlternatives(
            subject="Verification Plan XLSX file generated",
            from_email=settings.EMAIL_HOST_USER,
            to=[context["email"]],
            body=text_body,
        )
        email.attach_alternative(html_body, "text/html")
        result = email.send()
        if not result:
            logger.error(f"Email couldn't be send to {context['email']}")
