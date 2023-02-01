import logging
import zipfile
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

import openpyxl
from graphql import GraphQLError

from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    PaymentPlan,
)
from hct_mis_api.apps.payment.xlsx.base_xlsx_export_service import XlsxExportBaseService

if TYPE_CHECKING:
    from hct_mis_api.apps.account.models import User

logger = logging.getLogger(__name__)


class XlsxPaymentPlanExportPerFspService(XlsxExportBaseService):
    def __init__(self, payment_plan: PaymentPlan):
        self.payment_plan = payment_plan
        self.payment_list = payment_plan.not_excluded_payments.select_related(
            "household", "collector", "financial_service_provider"
        ).order_by("unicef_id")

    def export_per_fsp(self, user: "User") -> None:
        # TODO this should be refactored
        fsp_ids = self.payment_plan.delivery_mechanisms.values_list("financial_service_provider_id", flat=True)
        fsp_qs = FinancialServiceProvider.objects.filter(id__in=fsp_ids).distinct()
        if not fsp_qs:
            msg = (
                f"Not possible to generate export file. "
                f"There aren't any FSP(s) assigned to Payment Plan {self.payment_plan.unicef_id}."
            )
            logger.error(msg)
            raise GraphQLError(msg)

        # create temp zip file
        with NamedTemporaryFile() as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, mode="w") as zip_file:
                for fsp in fsp_qs:
                    wb = openpyxl.Workbook()
                    ws_fsp = wb.active
                    ws_fsp.title = fsp.name

                    payment_qs = self.payment_list.filter(financial_service_provider=fsp)

                    # get headers
                    column_list = list(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS)
                    template_column_list = []
                    if fsp.fsp_xlsx_template and fsp.fsp_xlsx_template.columns:
                        template_column_list = fsp.fsp_xlsx_template.columns
                        diff_columns = list(set(template_column_list).difference(set(column_list)))
                        if diff_columns:
                            msg = f"Please contact admin because we can't export columns: {diff_columns}"
                            logger.error(msg)
                            raise GraphQLError(msg)
                        column_list = list(template_column_list)

                    for core_field in fsp.fsp_xlsx_template.core_fields:
                        column_list.append(core_field)

                    # add headers
                    ws_fsp.append(column_list)

                    # add rows
                    for payment in payment_qs:
                        payment_row = [
                            FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(payment, column_name)
                            for column_name in template_column_list
                        ]
                        core_fields_row = [
                            FinancialServiceProviderXlsxTemplate.get_column_from_core_field(payment, column_name)
                            for column_name in fsp.fsp_xlsx_template.core_fields
                        ]
                        payment_row.extend(core_fields_row)
                        ws_fsp.append(payment_row)

                    self._adjust_column_width_from_col(ws_fsp, max_col=len(column_list))

                    filename = f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_{fsp.name}.xlsx"

                    with NamedTemporaryFile() as tmp:
                        wb.save(tmp.name)
                        tmp.seek(0)
                        # add xlsx to zip
                        zip_file.writestr(filename, tmp.read())

            zip_file_name = f"payment_plan_payment_list_{self.payment_plan.unicef_id}.zip"
            xlsx_obj = FileTemp(
                object_id=self.payment_plan.pk,
                content_type=get_content_type_for_model(self.payment_plan),
                created_by=user,
            )
            tmp_zip.seek(0)
            # remove old file
            self.payment_plan.remove_export_file()
            xlsx_obj.file.save(zip_file_name, File(tmp_zip))
            self.payment_plan.export_file = xlsx_obj
            self.payment_plan.save()
