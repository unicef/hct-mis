from page_object.base_components import BaseComponents


class TDetailsPage(BaseComponents):
  # Locators
  titlePage = 'h5[data-cy="page-header-title"]'
  status = 'div[data-cy="target-population-status"]'
  # Texts
  # Elements

  def getTitlePage(self):
        return self.wait_for(self.titlePage)

  def getStatus(self):
        return self.wait_for(self.status)
