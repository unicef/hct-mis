from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class RDIDetailsPage(BaseComponents):
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    labelStatus = 'div[data-cy="label-status"]'
    statusContainer = 'div[data-cy="status-container"]'
    labelSourceOfData = 'div[data-cy="label-Source of Data"]'
    labelImportDate = 'div[data-cy="label-Import Date"]'
    labelImportedBy = 'div[data-cy="label-Imported by"]'
    labelizedFieldContainerHouseholds = 'div[data-cy="labelized-field-container-households"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Households"]'
    labelizedFieldContainerIndividuals = 'div[data-cy="labelized-field-container-individuals"]'
    labelTotalNumberOfIndividuals = 'div[data-cy="label-Total Number of Individuals"]'
    tableLabel = 'span[data-cy="table-label"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    importedIndividualsTable = 'div[data-cy="imported-individuals-table"]'
    tableRow = 'tr[data-cy="table-row"]'
    buttonRefuseRdi = 'button[data-cy="button-refuse-rdi"]'
    buttonMergeRdi = 'button[data-cy="button-merge-rdi"]'

    # Texts
    buttonRefuseRdiText = "REFUSE IMPORT"
    buttonMergeRdiText = "MERGE"

    def getMainContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getLabelStatus(self) -> WebElement:
        return self.wait_for(self.labelStatus)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getLabelSourceOfData(self) -> WebElement:
        return self.wait_for(self.labelSourceOfData)

    def getLabelImportDate(self) -> WebElement:
        return self.wait_for(self.labelImportDate)

    def getLabelImportedBy(self) -> WebElement:
        return self.wait_for(self.labelImportedBy)

    def getLabelizedFieldContainerHouseholds(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerHouseholds)

    def getLabelTotalNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfHouseholds)

    def getLabelizedFieldContainerIndividuals(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerIndividuals)

    def getLabelTotalNumberOfIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfIndividuals)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getButtonRefuseRdi(self) -> WebElement:
        return self.wait_for(self.buttonRefuseRdi)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getButtonMergeRdi(self) -> WebElement:
        return self.wait_for(self.buttonMergeRdi)

    def getImportedIndividualsTable(self) -> WebElement:
        return self.wait_for(self.importedIndividualsTable)
