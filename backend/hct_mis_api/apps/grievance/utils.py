import logging
from typing import List, Union

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.models import Individual

logger = logging.getLogger(__name__)


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
    return individual


def select_individual(
    ticket_details: TicketNeedsAdjudicationDetails,
    selected_individual: Individual,
    ticket_duplicates: List[Individual],
    ticket_individuals: List[Individual],
) -> None:
    if selected_individual in ticket_duplicates and selected_individual not in ticket_individuals:
        ticket_details.selected_individuals.add(selected_individual)

        logger.info("Individual with id: %s added to ticket %s", str(selected_individual.id), str(ticket_details.id))


def traverse_sibling_tickets(grievance_ticket: GrievanceTicket, selected_individual: Individual) -> None:
    rdi = grievance_ticket.registration_data_import
    if not rdi:
        return

    sibling_tickets = GrievanceTicket.objects.filter(registration_data_import_id=rdi.id)

    for ticket in sibling_tickets:
        ticket_details = ticket.ticket_details
        ticket_duplicates = ticket_details.possible_duplicates.all()
        ticket_individuals = ticket_details.selected_individuals.all()

        select_individual(ticket_details, selected_individual, ticket_duplicates, ticket_individuals)


def clear_cache(
    ticket_details: Union[
        TicketHouseholdDataUpdateDetails,
        TicketDeleteHouseholdDetails,
        TicketAddIndividualDetails,
        TicketIndividualDataUpdateDetails,
        TicketDeleteIndividualDetails,
    ],
    business_area_slug: str,
) -> None:
    if isinstance(ticket_details, (TicketHouseholdDataUpdateDetails, TicketDeleteHouseholdDetails)):
        cache.delete_pattern(f"count_{business_area_slug}_HouseholdNodeConnection_*")

    if isinstance(
        ticket_details,
        (TicketAddIndividualDetails, TicketIndividualDataUpdateDetails, TicketDeleteIndividualDetails),
    ):
        cache.delete_pattern(f"count_{business_area_slug}_IndividualNodeConnection_*")
