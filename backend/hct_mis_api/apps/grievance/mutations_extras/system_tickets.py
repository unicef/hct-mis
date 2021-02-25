from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.grievance.mutations_extras.utils import (
    mark_as_duplicate_individual_and_reassign_roles,
)
from hct_mis_api.apps.household.models import Individual, UNIQUE, UNIQUE_IN_BATCH


def close_system_flagging_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.ticket_details

    if not ticket_details:
        return

    individual = ticket_details.golden_records_individual
    old_individual = copy_model_object(individual)

    if ticket_details.approve_status is False:
        individual.sanction_list_possible_match = False
        individual.save()
        log_create(
            Individual.ACTIVITY_LOG_MAPPING,
            "business_area",
            info.context.user,
            old_individual,
            individual,
        )
    else:
        individual.sanction_list_confirmed_match = True
        individual.save()


def _clear_deduplication_individuals_fields(individuals):
    for individual in individuals:
        individual.deduplication_golden_record_status = UNIQUE
        individual.deduplication_batch_status = UNIQUE_IN_BATCH
        individual.deduplication_golden_record_results = {}
        individual.deduplication_batch_results = {}
    Individual.objects.bulk_update(
        individuals,
        [
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
        ],
    )


def close_needs_adjudication_ticket(grievance_ticket, info):
    ticket_details = grievance_ticket.ticket_details

    if not ticket_details:
        return

    both_individuals = (ticket_details.golden_records_individual, ticket_details.possible_duplicate)

    if ticket_details.selected_individual is None:
        _clear_deduplication_individuals_fields(both_individuals)
    else:
        individual_to_remove = ticket_details.selected_individual
        unique_individuals = [individual for individual in both_individuals if individual.id != individual_to_remove.id]
        _clear_deduplication_individuals_fields(unique_individuals)
        mark_as_duplicate_individual_and_reassign_roles(
            ticket_details, individual_to_remove, info, unique_individuals[0]
        )
