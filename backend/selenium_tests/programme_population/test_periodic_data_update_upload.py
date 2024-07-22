from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from time import sleep
from typing import Any

import openpyxl
from django.conf import settings
from django.core.management import call_command

import pytest

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import PeriodicFieldData, FlexibleAttribute, BusinessArea
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate, PeriodicDataUpdateUpload
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PeriodicDataUpdateImportService,
)
from django.core.files import File

from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from page_object.programme_population.households import Households
from page_object.programme_population.households_details import HouseholdsDetails

from selenium_tests.page_object.programme_population.individuals import Individuals
from selenium_tests.tools.tag_name_finder import printing

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def program() -> Program:
    business_area = create_afghanistan()
    return ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=business_area)


@pytest.fixture
def individual(program: Program) -> Individual:
    business_area = create_afghanistan()
    rdi = RegistrationDataImportFactory()
    household, individuals = create_household_and_individuals(
        household_data={
            "business_area": business_area,
            "program_id": program.pk,
            "registration_data_import": rdi,
        },
        individuals_data=[
            {
                "business_area": business_area,
                "program_id": program.pk,
                "registration_data_import": rdi,
            },
        ],
    )
    return individuals[0]


@pytest.fixture
def string_attribute() -> FlexibleAttribute:
    return create_flexible_attribute(
        name="Test String Attribute",
        subtype=FlexibleAttribute.STRING,
        number_of_rounds=1,
        rounds_names=["Test Round"],
    )


@pytest.fixture
def date_attribute() -> FlexibleAttribute:
    return create_flexible_attribute(
        name="Test String Attribute",
        subtype=FlexibleAttribute.DATE,
        number_of_rounds=1,
        rounds_names=["Test Round"],
    )


def create_flexible_attribute(
    name: str, subtype: str, number_of_rounds: int, rounds_names: list[str]
) -> FlexibleAttribute:
    flexible_attribute = FlexibleAttribute.objects.create(
        name=name, type=FlexibleAttribute.PDU, associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


def add_pdu_data_to_xlsx(
    periodic_data_update_template: PeriodicDataUpdateTemplate, rows: list[list[Any]]
) -> _TemporaryFileWrapper:
    wb = openpyxl.load_workbook(periodic_data_update_template.file.file)
    ws_pdu = wb[PeriodicDataUpdateExportTemplateService.PDU_SHEET]
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            ws_pdu.cell(row=row_index + 2, column=col_index + 7, value=value)
    tmp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp_file.name)
    tmp_file.seek(0)
    return tmp_file


def prepare_xlsx_file(rounds_data: list, rows: list, program: Program) -> _TemporaryFileWrapper:
    periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
        program=program,
        business_area=program.business_area,
        filters=dict(),
        rounds_data=rounds_data,
    )
    service = PeriodicDataUpdateExportTemplateService(periodic_data_update_template)
    service.generate_workbook()
    service.save_xlsx_file()
    tmp_file = add_pdu_data_to_xlsx(periodic_data_update_template, rows)
    tmp_file.seek(0)
    return tmp_file


@pytest.mark.usefixtures("login")
class TestPeriodicDataUpdateUpload:
    def test_periodic_data_update_upload_success(
        self,
        program: Program,
        individual: Individual,
        string_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
    ) -> None:
        flexible_attribute = string_attribute
        tmp_file = prepare_xlsx_file(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["Test Value", "2021-05-02"]],
            program,
        )
        pageIndividuals.selectGlobalProgramFilter(program.name).click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        pageIndividuals.getButtonImport().click()
        pageIndividuals.getDialogImport()
        pageIndividuals.upload_file(tmp_file.name)
        pageIndividuals.getButtonImportSubmit().click()
        # TODO workaround to refresh
        pageIndividuals.driver.refresh()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        pageIndividuals.getPduUpdates().click()
        periodic_data_update_upload = PeriodicDataUpdateUpload.objects.first()
        assert periodic_data_update_upload.status == PeriodicDataUpdateUpload.Status.SUCCESSFUL
        assert periodic_data_update_upload.error_message == None
        individual.refresh_from_db()
        assert individual.flex_fields[flexible_attribute.name]["1"]["value"] == "Test Value"
        assert individual.flex_fields[flexible_attribute.name]["1"]["collection_date"] == "2021-05-02"
        assert pageIndividuals.getUpdateStatus(periodic_data_update_upload.pk).text == "SUCCESSFUL"

    def test_periodic_data_update_upload_form_error(
        self,
        program: Program,
        individual: Individual,
        date_attribute: FlexibleAttribute,
        pageIndividuals: Individuals,
    ) -> None:
        flexible_attribute = date_attribute
        tmp_file = prepare_xlsx_file(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["Test Value", "2021-05-02"]],
            program,
        )
        pageIndividuals.selectGlobalProgramFilter(program.name).click()
        pageIndividuals.getNavProgrammePopulation().click()
        pageIndividuals.getNavIndividuals().click()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        pageIndividuals.getButtonImport().click()
        pageIndividuals.getDialogImport()
        pageIndividuals.upload_file(tmp_file.name)
        pageIndividuals.getButtonImportSubmit().click()
        # TODO workaround to refresh
        pageIndividuals.driver.refresh()
        pageIndividuals.getTabPeriodicDataUpdates().click()
        pageIndividuals.getPduUpdates().click()
        periodic_data_update_upload = PeriodicDataUpdateUpload.objects.first()
        assert periodic_data_update_upload.status == PeriodicDataUpdateUpload.Status.FAILED
        assert pageIndividuals.getUpdateStatus(periodic_data_update_upload.pk).text == "FAILED"
        pageIndividuals.getUpdateDetailsBtn(periodic_data_update_upload.pk).click()
        error_text= "Row: 2\nTest String Attribute__round_value\nEnter a valid date."
        assert  pageIndividuals.getPduFormErrors().text == error_text
        # print(pageIndividuals.getPduFormErrors().text)
        # sleep(2)
        # printing("Mapping", pageIndividuals.driver)
        # printing("Methods", pageIndividuals.driver)
