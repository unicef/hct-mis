from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class DetailsTargeting(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonTargetPopulationDuplicate = 'button[data-cy="button-target-population-duplicate"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    buttonEdit = 'a[data-cy="button-edit"]'
    buttonRebuild = 'button[data-cy="button-rebuild"]'
    buttonTargetPopulationLock = 'button[data-cy="button-target-population-lock"]'
    detailsTitle = 'div[data-cy="details-title"]'
    detailsGrid = 'div[data-cy="details-grid"]'
    labelStatus = 'div[data-cy="label-Status"]'
    targetPopulationStatus = 'div[data-cy="target-population-status"]'
    labelizedFieldContainerCreatedBy = 'div[data-cy="labelized-field-container-created-by"]'
    labelCreatedBy = 'div[data-cy="label-created by"]'
    labelizedFieldContainerCloseDate = 'div[data-cy="labelized-field-container-close-date"]'
    labelProgrammePopulationCloseDate = 'div[data-cy="label-Programme population close date"]'
    labelizedFieldContainerProgramName = 'div[data-cy="labelized-field-container-program-name"]'
    labelProgramme = 'div[data-cy="label-Programme"]'
    labelizedFieldContainerSendBy = 'div[data-cy="labelized-field-container-send-by"]'
    labelSendBy = 'div[data-cy="label-Send by"]'
    labelizedFieldContainerSendDate = 'div[data-cy="labelized-field-container-send-date"]'
    labelSendDate = 'div[data-cy="label-Send date"]'
    criteriaContainer = 'div[data-cy="criteria-container"]'
    checkboxExcludeIfActiveAdjudicationTicket = 'span[data-cy="checkbox-exclude-if-active-adjudication-ticket"]'
    labelFemaleChildren = 'div[data-cy="label-Female Children"]'
    labelFemaleAdults = 'div[data-cy="label-Female Adults"]'
    labelMaleChildren = 'div[data-cy="label-Male Children"]'
    labelMaleAdults = 'div[data-cy="label-Male Adults"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Households"]'
    labelTargetedIndividuals = 'div[data-cy="label-Targeted Individuals"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    tablePagination = 'div[data-cy="table-pagination"]'

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonTargetPopulationDuplicate(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationDuplicate)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getButtonEdit(self) -> WebElement:
        return self.wait_for(self.buttonEdit)

    def getButtonRebuild(self) -> WebElement:
        return self.wait_for(self.buttonRebuild)

    def getButtonTargetPopulationLock(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationLock)

    def getDetailsTitle(self) -> WebElement:
        return self.wait_for(self.detailsTitle)

    def getDetailsGrid(self) -> WebElement:
        return self.wait_for(self.detailsGrid)

    def getLabelStatus(self) -> WebElement:
        return self.wait_for(self.labelStatus)

    def getTargetPopulationStatus(self) -> WebElement:
        return self.wait_for(self.targetPopulationStatus)

    def getLabelizedFieldContainerCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerCreatedBy)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelizedFieldContainerCloseDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerCloseDate)

    def getLabelProgrammePopulationCloseDate(self) -> WebElement:
        return self.wait_for(self.labelProgrammePopulationCloseDate)

    def getLabelizedFieldContainerProgramName(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerProgramName)

    def getLabelProgramme(self) -> WebElement:
        return self.wait_for(self.labelProgramme)

    def getLabelizedFieldContainerSendBy(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSendBy)

    def getLabelSendBy(self) -> WebElement:
        return self.wait_for(self.labelSendBy)

    def getLabelizedFieldContainerSendDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSendDate)

    def getLabelSendDate(self) -> WebElement:
        return self.wait_for(self.labelSendDate)

    def getCriteriaContainer(self) -> WebElement:
        return self.wait_for(self.criteriaContainer)

    def getCheckboxExcludeIfActiveAdjudicationTicket(self) -> WebElement:
        return self.wait_for(self.checkboxExcludeIfActiveAdjudicationTicket)

    def getLabelFemaleChildren(self) -> WebElement:
        return self.wait_for(self.labelFemaleChildren)

    def getLabelFemaleAdults(self) -> WebElement:
        return self.wait_for(self.labelFemaleAdults)

    def getLabelMaleChildren(self) -> WebElement:
        return self.wait_for(self.labelMaleChildren)

    def getLabelMaleAdults(self) -> WebElement:
        return self.wait_for(self.labelMaleAdults)

    def getLabelTotalNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfHouseholds)

    def getLabelTargetedIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTargetedIndividuals)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> WebElement:
        return self.get_elements(self.tableLabel)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
