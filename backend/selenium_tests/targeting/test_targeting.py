from datetime import datetime
from uuid import UUID

from django.conf import settings
from django.core.management import call_command

import pytest
from dateutil.relativedelta import relativedelta
from page_object.targeting.targeting import Targeting
from page_object.targeting.targeting_create import TargetingCreate
from page_object.targeting.targeting_details import TargetingDetails
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import (
    create_household,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import HEARING, HOST, REFUGEE, SEEING, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from selenium_tests.page_object.filters import Filters

pytestmark = pytest.mark.django_db(transaction=True, databases=["registration_datahub", "default"])


@pytest.fixture
def sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm", dct_type=DataCollectingType.Type.SOCIAL, status=Program.ACTIVE
    )


@pytest.fixture
def non_sw_program() -> Program:
    yield get_program_with_dct_type_and_name(
        "Test Programm", dct_type=DataCollectingType.Type.STANDARD, status=Program.ACTIVE
    )


def create_custom_household(observed_disability: list[str], residence_status: str = HOST) -> Household:
    program = Program.objects.get(name="Test Programm")
    household, _ = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-00-0000.0442",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "residence_status": residence_status,
        },
        individuals_data=[
            {
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
        ],
    )
    return household


@pytest.fixture
def household_with_disability() -> Household:
    yield create_custom_household(observed_disability=[SEEING, HEARING])


@pytest.fixture
def household_without_disabilities() -> Household:
    yield create_custom_household(observed_disability=[])


@pytest.fixture
def household_refugee() -> Household:
    yield create_custom_household(observed_disability=[], residence_status=REFUGEE)


def get_program_with_dct_type_and_name(
    name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.fixture
def create_targeting(household_without_disabilities: Household) -> TargetPopulation:
    program = Program.objects.first()
    target_population = TargetPopulation.objects.update_or_create(
        pk=UUID("00000000-0000-0000-0000-faceb00c0123"),
        name="Test Target Population",
        targeting_criteria=TargetingCriteriaFactory(),
        status=TargetPopulation.STATUS_OPEN,
        business_area=BusinessArea.objects.get(slug="afghanistan"),
        program=Program.objects.get(name="Test Programm"),
        created_by=User.objects.first(),
    )[0]
    target_population.save()
    household, _ = create_household(
        household_args={
            "unicef_id": "HH-00-0000.0442",
            "business_area": program.business_area,
            "program": program,
            "residence_status": HOST,
        },
    )
    target_population.households.set([household])
    yield target_population


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    yield


@pytest.fixture
def add_targeting() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/targeting/fixtures/data-cypress.json")
    yield


@pytest.mark.usefixtures("login")
class TestSmokeTargeting:
    def test_smoke_targeting_page(self, create_programs: None, add_targeting: None, pageTargeting: Targeting) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        assert "Targeting" in pageTargeting.getTitlePage().text
        assert "CREATE NEW" in pageTargeting.getButtonCreateNew().text
        expected_column_names = ["Name", "Status", "Num. of Households", "Date Created", "Last Edited", "Created by"]
        assert expected_column_names == [name.text for name in pageTargeting.getTabColumnLabel()]
        assert 2 == len(pageTargeting.getTargetPopulationsRows())
        pageTargeting.getButtonCreateNew().click()
        assert "Use Filters" in pageTargeting.getCreateUseFilters().text
        assert "Use IDs" in pageTargeting.getCreateUseIDs().text

    def test_smoke_targeting_create_use_filters(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageTargetingCreate: TargetingCreate
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseFilters().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getDivTargetPopulationAddCriteria().click()
        pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getButtonIndividualRule().click()
        pageTargetingCreate.getAutocompleteTargetCriteriaOption().click()

    def test_smoke_targeting_create_use_ids(
        self, create_programs: None, add_targeting: None, pageTargeting: Targeting, pageTargetingCreate: TargetingCreate
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputName()
        pageTargetingCreate.getInputIncludedHouseholdIds()
        pageTargetingCreate.getInputHouseholdids()
        pageTargetingCreate.getInputIncludedIndividualIds()
        pageTargetingCreate.getInputIndividualids()

    def test_smoke_targeting_details_page(
        self,
        create_programs: None,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        assert "Copy TP" in pageTargetingDetails.getPageHeaderTitle().text
        pageTargetingDetails.getButtonTargetPopulationDuplicate()
        pageTargetingDetails.getButtonDelete()
        assert "EDIT" in pageTargetingDetails.getButtonEdit().text
        assert "REBUILD" in pageTargetingDetails.getButtonRebuild().text
        assert "LOCK" in pageTargetingDetails.getButtonTargetPopulationLock().text
        assert "Details" in pageTargetingDetails.getDetailsTitle().text
        assert "OPEN" in pageTargetingDetails.getLabelStatus().text
        assert "OPEN" in pageTargetingDetails.getTargetPopulationStatus().text
        assert "CREATED BY" in pageTargetingDetails.getLabelizedFieldContainerCreatedBy().text
        pageTargetingDetails.getLabelCreatedBy()
        assert "PROGRAMME POPULATION CLOSE DATE" in pageTargetingDetails.getLabelizedFieldContainerCloseDate().text
        assert "PROGRAMME" in pageTargetingDetails.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageTargetingDetails.getLabelProgramme().text
        assert "SEND BY" in pageTargetingDetails.getLabelizedFieldContainerSendBy().text
        assert "-" in pageTargetingDetails.getLabelSendBy().text
        assert "-" in pageTargetingDetails.getLabelSendDate().text
        assert "-" in pageTargetingDetails.getCriteriaContainer().text
        assert "6" in pageTargetingDetails.getLabelFemaleChildren().text
        assert "1" in pageTargetingDetails.getLabelMaleChildren().text
        assert "2" in pageTargetingDetails.getLabelFemaleAdults().text
        assert "1" in pageTargetingDetails.getLabelMaleAdults().text
        assert "3" in pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        assert "7" in pageTargetingDetails.getLabelTargetedIndividuals().text
        assert "Households" in pageTargetingDetails.getTableTitle().text
        expected_menu_items = [
            "ID",
            "Head of Household",
            "Household Size",
            "Administrative Level 2",
            "Score",
        ]
        assert expected_menu_items == [i.text for i in pageTargetingDetails.getTableLabel()]


@pytest.mark.usefixtures("login")
class TestCreateTargeting:
    def test_create_targeting_for_people(
        self,
        sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", sw_program.id)
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD PEOPLE RULE"
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Does the Social Worker have disability?")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.select_multiple_option_by_name(HEARING, SEEING)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        disability_expected_criteria_text = "Does the Social Worker have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 2
        assert (
            pageTargetingDetails.getHouseholdTableCell(1, 1).text
            == household_with_disability.individuals.first().unicef_id
        )
        assert len(pageTargetingDetails.getPeopleTableRows()) == 1

    def test_create_targeting_for_normal_program(
        self,
        non_sw_program: Program,
        household_with_disability: Household,
        household_without_disabilities: Household,
        household_refugee: Household,
        pageTargeting: Targeting,
        pageTargetingCreate: TargetingCreate,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", non_sw_program.id)
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD HOUSEHOLD RULE"
        pageTargetingCreate.getAddHouseholdRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Residence Status")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.select_option_by_name(REFUGEE)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        disability_expected_criteria_text = "Residence status: Displaced | Refugee / Asylum Seeker"
        assert pageTargetingCreate.getCriteriaContainer().text == disability_expected_criteria_text
        targeting_name = "Test targeting people"
        pageTargetingCreate.getFieldName().send_keys(targeting_name)
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        pageTargetingDetails.getLockButton()
        assert pageTargetingDetails.getTitlePage().text == targeting_name
        assert pageTargetingDetails.getCriteriaContainer().text == disability_expected_criteria_text
        assert Household.objects.count() == 3
        assert Program.objects.count() == 1
        assert pageTargetingDetails.getHouseholdTableCell(1, 1).text == household_refugee.unicef_id
        actions = ActionChains(pageTargetingDetails.driver)
        actions.move_to_element(pageTargetingDetails.getHouseholdTableCell(1, 1)).perform()  # type: ignore
        assert len(pageTargetingDetails.getHouseholdTableRows()) == 1


@pytest.mark.usefixtures("login")
class TestTargeting:
    def test_targeting_create_use_ids_hh(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getInputName().send_keys(f"Target Population for {household_with_disability.unicef_id}")
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        target_population = TargetPopulation.objects.get(
            name=f"Target Population for {household_with_disability.unicef_id}"
        )
        assert (
            "1"
            == str(target_population.total_individuals_count)
            == pageTargetingDetails.getLabelTargetedIndividuals().text
        )
        assert (
            str(target_population.total_households_count) == pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        )
        assert str(target_population.status) in pageTargetingDetails.getLabelStatus().text

    def test_targeting_create_use_ids_individual(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        assert "New Target Population" in pageTargetingCreate.getPageHeaderTitle().text
        assert "SAVE" in pageTargetingCreate.getButtonTargetPopulationCreate().text
        pageTargetingCreate.getInputIndividualids().send_keys("IND-88-0000.0002")
        pageTargetingCreate.getInputName().send_keys("Target Population for IND-88-0000.0002")
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        target_population = TargetPopulation.objects.get(name="Target Population for IND-88-0000.0002")
        assert (
            "4"
            == str(target_population.total_individuals_count)
            == pageTargetingDetails.getLabelTargetedIndividuals().text
        )
        assert (
            str(target_population.total_households_count) == pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        )
        assert str(target_population.status) in pageTargetingDetails.getLabelStatus().text
        pageTargetingDetails.getButtonRebuild().click()

    def test_targeting_rebuild(
        self,
        create_programs: None,
        create_targeting: TargetPopulation,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getLabelStatus()
        pageTargetingDetails.getButtonRebuild().click()
        pageTargetingDetails.getStatusContainer()
        pageTargetingDetails.disappearStatusContainer()

    def test_targeting_mark_ready(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        filters: Filters,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        filters.selectFiltersSatus("OPEN")
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getLabelStatus()
        pageTargetingDetails.getLockButton().click()
        pageTargetingDetails.getLockPopupButton().click()
        pageTargetingDetails.waitForLabelStatus("LOCKED")
        pageTargetingDetails.getButtonMarkReady().click()
        pageTargetingDetails.getButtonPopupMarkReady().click()
        pageTargetingDetails.waitForLabelStatus("READY")

    def test_copy_targeting(
        self,
        create_programs: None,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        pageTargeting.selectGlobalProgramFilter(program.name).click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonTargetPopulationDuplicate().click()
        pageTargetingDetails.getInputName().send_keys("a1!")
        pageTargetingDetails.get_elements(pageTargetingDetails.buttonTargetPopulationDuplicate)[1].click()
        pageTargetingDetails.disappearInputName()
        assert "a1!" in pageTargetingDetails.getTitlePage().text
        assert "OPEN" in pageTargetingDetails.getTargetPopulationStatus().text
        assert "PROGRAMME" in pageTargetingDetails.getLabelizedFieldContainerProgramName().text
        assert "Test Programm" in pageTargetingDetails.getLabelProgramme().text
        assert "2" in pageTargetingDetails.getLabelTotalNumberOfHouseholds().text
        assert "8" in pageTargetingDetails.getLabelTargetedIndividuals().text

    def test_edit_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonEdit().click()
        pageTargetingDetails.getInputName().send_keys(Keys.CONTROL + "a")
        pageTargetingDetails.getInputName().send_keys("New Test Data")
        pageTargetingDetails.getButtonIconEdit().click()
        pageTargetingDetails.getHouseholdSizeFrom().send_keys(Keys.CONTROL + "a")
        pageTargetingDetails.getHouseholdSizeFrom().send_keys("0")
        pageTargetingDetails.getHouseholdSizeTo().send_keys(Keys.CONTROL + "a")
        pageTargetingDetails.getHouseholdSizeTo().send_keys("9")
        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()
        pageTargetingCreate.getButtonSave().click()
        pageTargetingDetails.getButtonEdit()
        assert pageTargetingDetails.waitForTextTitlePage("New Test Data")
        assert "9" in pageTargetingDetails.getCriteriaContainer().text

    def test_delete_targeting(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.disappearLoadingRows()
        old_list = pageTargeting.getTargetPopulationsRows()
        assert 2 == len(old_list)
        assert "Copy TP" in old_list[0].text

        pageTargeting.chooseTargetPopulations(0).click()
        pageTargetingDetails.getButtonDelete().click()
        pageTargetingDetails.getDialogBox()
        pageTargetingDetails.get_elements(pageTargetingDetails.buttonDelete)[1].click()
        pageTargeting.disappearLoadingRows()
        new_list = pageTargeting.getTargetPopulationsRows()
        assert 1 == len(new_list)
        assert "Test NEW TP" in new_list[0].text

    def test_targeting_different_program_statuses(
        self,
        create_programs: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.status = Program.DRAFT
        program.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.mouse_on_element(pageTargeting.getButtonInactiveCreateNew())
        assert "Program has to be active to create a new Target Population" in pageTargeting.geTooltip().text
        program.status = Program.ACTIVE
        program.save()
        pageTargeting.driver.refresh()
        pageTargeting.getButtonCreateNew()
        program.status = Program.FINISHED
        program.save()
        pageTargeting.driver.refresh()
        pageTargeting.mouse_on_element(pageTargeting.getButtonInactiveCreateNew())
        assert "Program has to be active to create a new Target Population" in pageTargeting.geTooltip().text

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "type": "SOCIAL",
                    "text": "Exclude People with Active Adjudication Ticket",
                },
                id="People",
            ),
            pytest.param(
                {
                    "type": "STANDARD",
                    "text": "Exclude Households with Active Adjudication Ticket",
                },
                id="Program population",
            ),
        ],
    )
    def test_exclude_households_with_active_adjudication_ticket(
        self,
        test_data: dict,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getInputName().send_keys(f"Test {household_with_disability.unicef_id}")
        pageTargetingCreate.getInputFlagexcludeifactiveadjudicationticket().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        with pytest.raises(NoSuchElementException):
            pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
        if test_data["type"] == "SOCIAL":
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket()
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
            assert (
                test_data["text"]
                in pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket()
                .find_element(By.XPATH, "./..")
                .text
            )
        elif test_data["type"] == "STANDARD":
            pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket()
            pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )
            assert (
                test_data["text"]
                in pageTargetingDetails.getCheckboxExcludeIfActiveAdjudicationTicket()
                .find_element(By.XPATH, "./..")
                .text
            )

    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "type": "SOCIAL",
                    "text": "Exclude People with an active sanction screen flag",
                },
                id="People",
            ),
            pytest.param(
                {
                    "type": "STANDARD",
                    "text": "Exclude Households with an active sanction screen flag",
                },
                id="Program population",
            ),
        ],
    )
    def test_exclude_households_with_sanction_screen_flag(
        self,
        test_data: dict,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        program = Program.objects.get(name="Test Programm")
        program.data_collecting_type.type = test_data["type"]
        program.data_collecting_type.save()
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getCreateUseIDs().click()
        pageTargetingCreate.getInputHouseholdids().send_keys(household_with_disability.unicef_id)
        pageTargetingCreate.getInputName().send_keys(f"Test {household_with_disability.unicef_id}")
        pageTargetingCreate.getInputFlagexcludeifonsanctionlist().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        pageTargetingDetails.getCheckboxExcludeIfOnSanctionList()
        # ToDo: Add after merge to develop
        # assert (
        #     test_data["text"]
        #     in pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(By.XPATH, "./..").text
        # )
        pageTargetingDetails.getCheckboxExcludeIfOnSanctionList().find_element(
            By.CSS_SELECTOR, pageTargetingDetails.iconSelected
        )
        with pytest.raises(NoSuchElementException):
            pageTargetingDetails.getCheckboxExcludePeopleIfActiveAdjudicationTicket().find_element(
                By.CSS_SELECTOR, pageTargetingDetails.iconSelected
            )

    def test_targeting_info_button(
        self,
        create_programs: None,
        pageTargeting: Targeting,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonTargetPopulation().click()
        pageTargeting.getTabFieldList()
        pageTargeting.getTabTargetingDiagram().click()

    def test_targeting_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        filters: Filters,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        filters.getFiltersSearch().send_keys("Copy")
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(1)
        assert "OPEN" in pageTargeting.getStatusContainer().text
        filters.getButtonFiltersClear().click()
        filters.getFiltersStatus().click()
        filters.select_listbox_element("Open").click()
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(1)
        assert "OPEN" in pageTargeting.getStatusContainer().text
        filters.getButtonFiltersClear().click()
        filters.getFiltersTotalHouseholdsCountMin().send_keys("10")
        filters.getFiltersTotalHouseholdsCountMax().send_keys("10")
        filters.getButtonFiltersApply().click()
        pageTargeting.countTargetPopulations(0)
        filters.getButtonFiltersClear().click()
        filters.getFiltersTotalHouseholdsCountMin().send_keys("1")
        filters.getFiltersTotalHouseholdsCountMax().send_keys("3")
        pageTargeting.countTargetPopulations(2)
        filters.getButtonFiltersClear().click()

    def test_targeting_and_labels(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getColumnName().click()
        pageTargeting.disappearLoadingRows()
        assert "Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnName().click()
        pageTargeting.disappearLoadingRows()
        assert "Test NEW TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnStatus().click()
        pageTargeting.disappearLoadingRows()
        assert "Test NEW TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnStatus().click()
        pageTargeting.disappearLoadingRows()
        assert "Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnNumOfHouseholds().click()
        pageTargeting.disappearLoadingRows()
        assert "Test NEW TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnDateCreated().click()
        pageTargeting.disappearLoadingRows()
        assert "Test NEW TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnDateCreated().click()
        pageTargeting.disappearLoadingRows()
        assert "Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnLastEdited().click()
        pageTargeting.disappearLoadingRows()
        assert "Test NEW TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnLastEdited().click()
        pageTargeting.disappearLoadingRows()
        assert "Copy TP" in pageTargeting.chooseTargetPopulations(0).text
        pageTargeting.getColumnCreatedBy().click()
        pageTargeting.disappearLoadingRows()
        assert "est NEW TP" in pageTargeting.chooseTargetPopulations(0).text

    def test_targeting_parametrized_rules_filters(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Females Age 0 - 5").click()
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("0")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getButtonTargetPopulationAddCriteria().click()
        pageTargetingCreate.getInputName().send_keys("Target Population for Females Age 0 - 5")
        pageTargetingCreate.getInputFlagexcludeifactiveadjudicationticket().click()
        pageTargetingCreate.clickButtonTargetPopulationCreate()
        assert "Females Age 0 - 5: 11" in pageTargetingCreate.getCriteriaContainer().text

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_targeting_parametrized_rules_filters_and_or(
        self,
        create_programs: None,
        household_with_disability: Household,
        add_targeting: None,
        pageTargeting: Targeting,
        pageTargetingDetails: TargetingDetails,
        pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.selectGlobalProgramFilter("Test Programm").click()
        pageTargeting.getNavTargeting().click()
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Females Age 0 - 5").click()
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("0")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("1")
        pageTargetingCreate.getButtonHouseholdRule().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete(1).click()
        pageTargetingCreate.select_listbox_element("Village").click()
        pageTargetingCreate.getInputFiltersValue(1).send_keys("Testtown")
        pageTargetingCreate.getButtonIndividualRule().click()
        pageTargetingCreate.getTargetingCriteriaAutoCompleteIndividual().click()
        pageTargetingCreate.select_listbox_element("Does the Individual have disability?").click()
        pageTargetingCreate.getSelectMany().click()
        pageTargetingCreate.select_multiple_option_by_name(HEARING, SEEING)
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        assert "Females Age 0 - 5: 1" in pageTargetingCreate.getCriteriaContainer().text
        assert "Village: Testtown" in pageTargetingCreate.getCriteriaContainer().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in pageTargetingCreate.getCriteriaContainer().text
        )
        pageTargetingCreate.getButtonEdit().click()
        pageTargetingCreate.getTargetingCriteriaAutoCompleteIndividual()
        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()
        pageTargetingCreate.getInputName().send_keys("Target Population")
        assert "ADD 'OR'FILTER" in pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().text
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.getAddHouseholdRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.select_listbox_element("Males age 0 - 5 with disability").click()
        pageTargetingCreate.getInputFiltersValueFrom(0).send_keys("1")
        pageTargetingCreate.getInputFiltersValueTo(0).send_keys("10")
        pageTargetingCreate.get_elements(pageTargetingCreate.targetingCriteriaAddDialogSaveButton)[1].click()
        pageTargetingCreate.getTargetPopulationSaveButton().click()
        assert "Females Age 0 - 5: 1" in pageTargetingCreate.getCriteriaContainer().text
        assert "Village: Testtown" in pageTargetingCreate.getCriteriaContainer().text
        assert (
            "Does the Individual have disability?: Difficulty hearing (even if using a hearing aid), Difficulty seeing (even if wearing glasses)"
            in pageTargetingCreate.getCriteriaContainer().text
        )
        assert (
            "Males age 0 - 5 with disability: 1 -10"
            in pageTargetingCreate.get_elements(pageTargetingCreate.criteriaContainer)[1].text
        )
