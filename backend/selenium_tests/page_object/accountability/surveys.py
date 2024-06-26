from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class SurveysPage(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    rows = 'tr[role="checkbox"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'

    # Texts
    textTitlePage = "Surveys"
    textNewSurvey = "New Survey"
    textTargetPopulationFilter = "Target Population"
    textTabCreatedBy = "Created by"

    # Elements
    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getMessageID(self) -> WebElement:
        return self.wait_for(self.tabColumnLabel).eq(0)

    def getApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getTargetPopulationsRows(self) -> WebElement:
        return self.wait_for(self.rows)
