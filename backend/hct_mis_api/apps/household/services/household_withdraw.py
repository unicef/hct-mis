from django.db.models import QuerySet

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual


class HouseholdWithdraw:
    def __init__(self, household: Household):
        self.household: Household = household
        self.individuals: QuerySet[Individual] = self.household.individuals.filter(duplicate=False)
        self.documents = None

    def withdraw(self):
        self.household.withdraw()

        for individual in self.individuals:
            individual.withdraw()

    def unwithdraw(self):
        self.household.unwithdraw()

        for individual in self.individuals:
            individual.unwithdraw()

    def change_tickets_status(self, tickets):
        for ticket in tickets:
            if self.household.withdrawn:
                ticket.ticket.extras["status_before_withdrawn"] = ticket.ticket.status
                ticket.ticket.status = GrievanceTicket.STATUS_CLOSED
            elif ticket.ticket.extras.get("status_before_withdrawn"):
                ticket.ticket.status = ticket.ticket.extras["status_before_withdrawn"]
                ticket.ticket.extras["status_before_withdrawn"] = ""
            ticket.ticket.save()
