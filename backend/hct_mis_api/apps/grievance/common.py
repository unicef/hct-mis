import logging
from typing import List, Optional, Tuple

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification

logger = logging.getLogger(__name__)


def _get_min_max_score(golden_records) -> Tuple[float, float]:
    items = [item.get("score", 0.0) for item in golden_records]

    return min(items, default=0.0), max(items, default=0.0)


def create_grievance_ticket_with_details(
    main_individual,
    possible_duplicate,
    business_area,
    possible_duplicates=None,
    registration_data_import=None,
    is_multiple_duplicates_version=False,
) -> Tuple[Optional[GrievanceTicket], Optional[TicketNeedsAdjudicationDetails]]:
    from hct_mis_api.apps.grievance.models import (
        GrievanceTicket,
        TicketNeedsAdjudicationDetails,
    )

    if not possible_duplicates:
        return None, None

    ticket_all_individuals = {main_individual, *possible_duplicates}

    ticket_already_exists = (
        TicketNeedsAdjudicationDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .filter(golden_records_individual__in=ticket_all_individuals, possible_duplicates__in=ticket_all_individuals)
        .exists()
    )

    if ticket_already_exists:
        return None, None

    household = main_individual.household
    admin_level_2 = household.admin2 if household else None
    area = household.village if household else ""

    ticket = GrievanceTicket.objects.create(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        business_area=business_area,
        admin2=admin_level_2,
        area=area,
        registration_data_import=registration_data_import,
    )
    golden_records = main_individual.get_deduplication_golden_record()
    extra_data = {
        "golden_records": golden_records,
        "possible_duplicate": possible_duplicate.get_deduplication_golden_record(),
    }
    score_min, score_max = _get_min_max_score(golden_records)
    ticket_details = TicketNeedsAdjudicationDetails.objects.create(
        ticket=ticket,
        golden_records_individual=main_individual,
        possible_duplicate=possible_duplicate,
        is_multiple_duplicates_version=is_multiple_duplicates_version,
        selected_individual=None,
        extra_data=extra_data,
        score_min=score_min,
        score_max=score_max,
    )

    ticket_details.possible_duplicates.add(*possible_duplicates)

    GrievanceNotification.send_all_notifications(GrievanceNotification.prepare_notification_for_ticket_creation(ticket))

    return ticket, ticket_details


def create_needs_adjudication_tickets(
    individuals_queryset, results_key, business_area, registration_data_import=None
) -> Optional[List[TicketNeedsAdjudicationDetails]]:
    from hct_mis_api.apps.household.models import Individual

    if not individuals_queryset:
        return None

    ticket_details_to_create = []
    for possible_duplicate in individuals_queryset:
        linked_tickets = []
        possible_duplicates = []

        for individual in possible_duplicate.deduplication_golden_record_results[results_key]:
            duplicate = Individual.objects.filter(id=individual.get("hit_id")).first()
            if not duplicate:
                continue

            possible_duplicates.append(duplicate)

        ticket, ticket_details = create_grievance_ticket_with_details(
            main_individual=possible_duplicate,
            possible_duplicate=possible_duplicate,  # for backward compatibility
            business_area=business_area,
            registration_data_import=registration_data_import,
            possible_duplicates=possible_duplicates,
            is_multiple_duplicates_version=True,
        )

        if ticket and ticket_details:
            linked_tickets.append(ticket)
            ticket_details_to_create.append(ticket_details)

        for ticket in linked_tickets:
            ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])

    return ticket_details_to_create
