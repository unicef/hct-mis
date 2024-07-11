from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.grievance.services.reassign_roles_services import (
    reassign_roles_on_disable_individual_service,
)
from hct_mis_api.apps.grievance.signals import (
    individual_marked_as_distinct,
    individual_marked_as_duplicated,
)
from hct_mis_api.apps.grievance.utils import (
    traverse_sibling_tickets,
    validate_all_individuals_before_close_needs_adjudication,
)
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.models import (
    UNIQUE,
    UNIQUE_IN_BATCH,
    Household,
    Individual,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.program.models import Program


def _clear_deduplication_individuals_fields(individuals: Sequence[Individual]) -> None:
    for individual in individuals:
        individual.deduplication_golden_record_status = UNIQUE
        individual.deduplication_batch_status = UNIQUE_IN_BATCH
        individual.deduplication_golden_record_results = {}
        individual.deduplication_batch_results = {}
        HardDocumentDeduplication().deduplicate(individual.documents.all())
    Individual.objects.bulk_update(
        individuals,
        [
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
        ],
    )


def close_needs_adjudication_old_ticket(ticket_details: TicketNeedsAdjudicationDetails, user: AbstractUser) -> None:
    both_individuals = (ticket_details.golden_records_individual, ticket_details.possible_duplicate)

    if ticket_details.selected_individual is None:
        _clear_deduplication_individuals_fields(both_individuals)
    else:
        individual_to_remove = ticket_details.selected_individual
        unique_individuals = [individual for individual in both_individuals if individual.id != individual_to_remove.id]
        mark_as_duplicate_individual_and_reassign_roles(
            ticket_details, individual_to_remove, user, unique_individuals[0]
        )
        _clear_deduplication_individuals_fields(unique_individuals)


def close_needs_adjudication_new_ticket(ticket_details: TicketNeedsAdjudicationDetails, user: AbstractUser) -> None:
    # TODO: need to double check all this logic here
    validate_all_individuals_before_close_needs_adjudication(ticket_details)

    distinct_individuals = ticket_details.selected_distinct.all()
    duplicate_individuals = ticket_details.possible_duplicates.all()

    if duplicate_individuals:
        for individual_to_remove in duplicate_individuals:
            mark_as_duplicate_individual_and_reassign_roles(ticket_details, individual_to_remove, user)
        _clear_deduplication_individuals_fields(duplicate_individuals)

    if distinct_individuals:
        for individual_to_distinct in distinct_individuals:
            mark_as_distinct_and_reassign_roles(ticket_details, individual_to_distinct, user)
        _clear_deduplication_individuals_fields(distinct_individuals)


def close_needs_adjudication_ticket_service(grievance_ticket: GrievanceTicket, user: AbstractUser) -> None:
    # TODO: check this one
    ticket_details = grievance_ticket.ticket_details
    if not ticket_details:
        return

    if ticket_details.is_multiple_duplicates_version:
        # selected_individuals - will use in future maybe 'selected_duplicates'

        selected_duplicates = ticket_details.selected_individuals.all()
        # selected_distinct = ticket_details.selected_distinct.all()
        traverse_sibling_tickets(grievance_ticket, selected_duplicates)
        # traverse_sibling_tickets(grievance_ticket, selected_distinct)  # TODO: have to check it
        close_needs_adjudication_new_ticket(ticket_details, user)
    else:
        close_needs_adjudication_old_ticket(ticket_details, user)


def _get_min_max_score(golden_records: List[Dict]) -> Tuple[float, float]:
    items = [item.get("score", 0.0) for item in golden_records]

    return min(items, default=0.0), max(items, default=0.0)


def create_grievance_ticket_with_details(
    main_individual: Individual,
    possible_duplicate: Individual,
    business_area: BusinessArea,
    possible_duplicates: Optional[List[Individual]] = None,
    registration_data_import: Optional[RegistrationDataImport] = None,
    is_multiple_duplicates_version: bool = False,
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
    ticket.programs.set([main_individual.program])
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
    ticket_details.populate_cross_area_flag()

    GrievanceNotification.send_all_notifications(GrievanceNotification.prepare_notification_for_ticket_creation(ticket))

    return ticket, ticket_details


def create_needs_adjudication_tickets(
    individuals_queryset: QuerySet[Individual],
    results_key: str,
    business_area: BusinessArea,
    registration_data_import: Optional[RegistrationDataImport] = None,
) -> None:
    from hct_mis_api.apps.household.models import Individual

    if not individuals_queryset:
        return None

    unique_individuals = set()
    individuals_to_remove_from_es = set()
    for possible_duplicate in individuals_queryset:
        possible_duplicates = []

        for individual in possible_duplicate.deduplication_golden_record_results[results_key]:
            if duplicate := Individual.objects.filter(id=individual.get("hit_id")).first():
                possible_duplicates.append(duplicate)
            else:
                individuals_to_remove_from_es.add(individual.get("hit_id"))

        if possible_duplicates and not (possible_duplicate in possible_duplicates and len(possible_duplicates) == 1):
            ticket, ticket_details = create_grievance_ticket_with_details(
                main_individual=possible_duplicate,
                possible_duplicate=possible_duplicate,  # for backward compatibility
                business_area=business_area,
                registration_data_import=registration_data_import,
                possible_duplicates=possible_duplicates,
                is_multiple_duplicates_version=True,
            )

            linked_tickets = []
            if ticket and ticket_details:
                linked_tickets.append(ticket)

            for ticket in linked_tickets:
                ticket.linked_tickets.set([t for t in linked_tickets if t != ticket])
        else:
            unique_individuals.add(possible_duplicate.id)

    # Sometimes we have an old records in the Elasticsearch, this will resolve false positive signals if the individual is indeed unique
    Individual.objects.filter(id__in=unique_individuals).update(
        deduplication_golden_record_status=UNIQUE, deduplication_golden_record_results={}
    )
    doc = get_individual_doc(business_area.slug)
    remove_elasticsearch_documents_by_matching_ids(list(individuals_to_remove_from_es), doc)


def mark_as_duplicate_individual_and_reassign_roles(
    ticket_details: TicketNeedsAdjudicationDetails,
    individual_to_remove: Individual,
    user: AbstractUser,
    unique_individual: Optional[Individual] = None,
) -> None:
    if ticket_details.is_multiple_duplicates_version:
        household = reassign_roles_on_disable_individual_service(
            individual_to_remove,
            ticket_details.role_reassign_data,
            user,
            ticket_details.ticket.programs.all(),
            "new_individual",
        )
    else:
        household = reassign_roles_on_disable_individual_service(
            individual_to_remove, ticket_details.role_reassign_data, user, ticket_details.ticket.programs.all()
        )
    mark_as_duplicate_individual(
        individual_to_remove, unique_individual, household, user, ticket_details.ticket.programs.all()
    )


def mark_as_distinct_and_reassign_roles(
    ticket_details: TicketNeedsAdjudicationDetails,
    individual_to_distinct: Individual,
    user: AbstractUser,
) -> None:
    # TODO: HAVE to update this logic
    if ticket_details.is_multiple_duplicates_version:
        household = reassign_roles_on_disable_individual_service(
            individual_to_distinct,
            ticket_details.role_reassign_data,
            user,
            ticket_details.ticket.programs.all(),
            "new_individual",
        )
    else:
        household = reassign_roles_on_disable_individual_service(
            individual_to_distinct, ticket_details.role_reassign_data, user, ticket_details.ticket.programs.all()
        )
    mark_as_distinct_individual(individual_to_distinct, household, user, ticket_details.ticket.programs.all())


def mark_as_duplicate_individual(
    individual_to_remove: Individual,
    unique_individual: Optional[Individual],
    household: Optional[Household],
    user: AbstractUser,
    program: "Program",
) -> None:
    old_individual = Individual.objects.get(id=individual_to_remove.id)
    # TODO: who is unique_individual is more then 1 was selected.. or none just
    individual_to_remove.mark_as_duplicate(unique_individual)
    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        user,
        getattr(program, "pk", None),
        old_individual,
        individual_to_remove,
    )
    individual_marked_as_duplicated.send(sender=Individual, instance=individual_to_remove)
    if household:
        household.refresh_from_db()
        if household.active_individuals.count() == 0:
            household.withdraw()


def mark_as_distinct_individual(
    individual_to_distinct: Individual,
    household: Optional[Household],
    user: AbstractUser,
    program: "Program",
) -> None:
    old_individual = Individual.objects.get(id=individual_to_distinct.id)
    # TODO: who is unique_individual is more then 1 was selected.. or just None
    individual_to_distinct.mark_as_distinct()
    log_create(
        Individual.ACTIVITY_LOG_MAPPING,
        "business_area",
        user,
        getattr(program, "pk", None),
        old_individual,
        individual_to_distinct,
    )
    individual_marked_as_distinct.send(sender=Individual, instance=individual_to_distinct)
    if household:
        household.refresh_from_db()
        if household.active_individuals.count() > 0:
            household.unwithdraw()
