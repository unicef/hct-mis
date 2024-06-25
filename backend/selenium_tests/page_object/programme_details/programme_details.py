from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgrammeDetails(BaseComponents):
    headerTitle = 'h5[data-cy="page-header-title"]'
    copyProgram = 'a[data-cy="button-copy-program"]'
    programStatus = 'div[data-cy="status-container"]'
    labelStartDate = 'div[data-cy="label-START DATE"]'
    labelEndDate = 'div[data-cy="label-END DATE"]'
    labelSelector = 'div[data-cy="label-Sector"]'
    labelDataCollectingType = 'div[data-cy="label-Data Collecting Type"]'
    labelFreqOfPayment = 'div[data-cy="label-Frequency of Payment"]'
    labelAdministrativeAreas = 'div[data-cy="label-Administrative Areas of implementation"]'
    labelCashPlus = 'div[data-cy="label-CASH+"]'
    labelProgramSize = 'div[data-cy="label-Program size"]'
    labelDescription = 'div[data-cy="label-Description"]'
    labelAreaAccess = 'div[data-cy="label-Area Access"]'
    labelAdminArea1 = 'div[data-cy="labelized-field-container-admin-area-1-total-count"]'
    labelAdminArea2 = 'div[data-cy="label-Admin Area 2"]'
    labelPartnerName = 'h6[data-cy="label-partner-name"]'
    labelPartnerAccess = 'div[data-cy="label-Partner Access"]'
    buttonRemoveProgram = 'button[data-cy="button-remove-program"]'
    buttonEditProgram = 'a[data-cy="button-edit-program"]'
    buttonActivateProgram = 'button[data-cy="button-activate-program"]'
    labelProgrammeCode = 'div[data-cy="label-Programme Code"]'
    buttonFinishProgram = 'button[data-cy="button-finish-program"]'

    def getLabelPartnerName(self) -> WebElement:
        return self.wait_for(self.labelPartnerName)

    def getLabelAreaAccess(self) -> WebElement:
        return self.wait_for(self.labelAreaAccess)

    def getLabelPartnerAccess(self) -> WebElement:
        return self.wait_for(self.labelPartnerAccess)

    def getLabelAdminArea1(self) -> WebElement:
        return self.wait_for(self.labelAdminArea1)

    def getLabelAdminArea2(self) -> WebElement:
        return self.wait_for(self.labelAdminArea2)

    def getProgramStatus(self) -> WebElement:
        return self.wait_for(self.programStatus)

    def getHeaderTitle(self) -> WebElement:
        return self.wait_for(self.headerTitle)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getLabelSelector(self) -> WebElement:
        return self.wait_for(self.labelSelector)

    def getLabelDataCollectingType(self) -> WebElement:
        return self.wait_for(self.labelDataCollectingType)

    def getLabelFreqOfPayment(self) -> WebElement:
        return self.wait_for(self.labelFreqOfPayment)

    def getLabelAdministrativeAreas(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeAreas)

    def getLabelCashPlus(self) -> WebElement:
        return self.wait_for(self.labelCashPlus)

    def getLabelProgramSize(self) -> WebElement:
        return self.wait_for(self.labelProgramSize)

    def getCopyProgram(self) -> WebElement:
        return self.wait_for(self.copyProgram)

    def getLabelDescription(self) -> WebElement:
        return self.wait_for(self.labelDescription)

    def getButtonRemoveProgram(self) -> WebElement:
        return self.wait_for(self.buttonRemoveProgram)

    def getButtonEditProgram(self) -> WebElement:
        return self.wait_for(self.buttonEditProgram)

    def getButtonActivateProgram(self) -> WebElement:
        return self.wait_for(self.buttonActivateProgram)

    def getLabelProgrammeCode(self) -> WebElement:
        return self.wait_for(self.labelProgrammeCode)

    def getButtonFinishProgram(self) -> WebElement:
        return self.wait_for(self.buttonFinishProgram)

    def getButtonFinishProgramPopup(self) -> WebElement:
        self.wait_for('[data-cy="dialog-actions-container"]')
        return self.get_elements(self.buttonFinishProgram)[1]
