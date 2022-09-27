import logging
from typing import List

from django.shortcuts import get_object_or_404

from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails, GrievanceDocument
from hct_mis_api.apps.grievance.validators import validate_file
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.core.utils import decode_id_string

logger = logging.getLogger(__name__)


def get_individual(individual_id: str) -> Individual:
    decoded_selected_individual_id = decode_id_string(individual_id)
    individual = get_object_or_404(Individual, id=decoded_selected_individual_id)
    return individual


def select_individual(
    ticket_details: TicketNeedsAdjudicationDetails,
    selected_individual: List[Individual],
    ticket_duplicates: List[Individual],
    ticket_individuals: List[Individual],
):
    if selected_individual in ticket_duplicates and selected_individual not in ticket_individuals:
        ticket_details.selected_individuals.add(selected_individual)

        logger.info("Individual with id: %s added to ticket %s", str(selected_individual.id), str(ticket_details.id))


def traverse_sibling_tickets(grievance_ticket: GrievanceTicket, selected_individual: Individual):
    sibling_tickets = GrievanceTicket.objects.filter(
        registration_data_import_id=grievance_ticket.registration_data_import.id
    )

    for ticket in sibling_tickets:
        ticket_details = ticket.ticket_details
        ticket_duplicates = ticket_details.possible_duplicates.all()
        ticket_individuals = ticket_details.selected_individuals.all()

        select_individual(ticket_details, selected_individual, ticket_duplicates, ticket_individuals)


def create_grievance_documents(info, grievance_ticket, documents):
    grievance_documents = []
    for document in documents:
        file = document["file"]
        validate_file(file)

        grievance_document = GrievanceDocument(
            name=document["name"],
            file=file,
            created_by=info.context.user,
            grievance_ticket=grievance_ticket,
            file_size=file.size,
            content_type=file.content_type,
        )
        grievance_documents.append(grievance_document)
    GrievanceDocument.objects.bulk_create(grievance_documents)


def update_grievance_documents(documents):
    for document in documents:
        ticket_id = document["id"]
        current_document_qs = GrievanceDocument.objects.filter(id=ticket_id)
        current_document = current_document_qs.first()

        if current_document:
            name = document.get("name", current_document.name)
            file = document.get("file", current_document.file)
            validate_file(file)

            current_document_qs.update(name=name, file=file, file_size=file.size, content_type=file.content_type)
