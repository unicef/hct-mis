from page_object.base_components import BaseComponents


class GrievanceDashboard(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    userGenerated = 'div[data-cy="label-USER-GENERATED"]'
    systemGenerated = 'div[data-cy="label-SYSTEM-GENERATED"]'
    averageResolution = 'div[data-cy="tickets-average-resolution-top-number"]'
    totalClosed = 'div[data-cy="total-number-of-closed-tickets-top-number"]'
    totalTickets = 'div[data-cy="total-number-of-tickets-top-number"]'
    # Texts
    textTitle = "Grievance Dashboard"
    # Elements

    def Title(self):
        return self.wait_for(self.titlePage)

    def getAverageResolution(self):
        return self.wait_for(self.averageResolution)

    def getTotalClosed(self):
        return self.wait_for(self.totalClosed)

    def getTotalTickets(self):
        return self.wait_for(self.totalTickets)

    def getUserGeneratedResolutions(self):
        return self.wait_for(self.userGenerated).eq(2)

    def getUserGeneratedClosed(self):
        return self.wait_for(self.userGenerated).eq(1)

    def getUserGeneratedTickets(self):
        return self.wait_for(self.userGenerated).eq(0)

    def getSystemGeneratedResolutions(self):
        return self.wait_for(self.systemGenerated).eq(2)

    def getSystemGeneratedClosed(self):
        return self.wait_for(self.systemGenerated).eq(1)

    def getSystemGeneratedTickets(self):
        return self.wait_for(self.systemGenerated).eq(0)
