from django.db import transaction

from grievance.common import create_needs_adjudication_tickets
from grievance.models import TicketNeedsAdjudicationDetails
from household.documents import IndividualDocument
from household.elasticsearch_utils import populate_index
from household.models import Individual, DUPLICATE, NEEDS_ADJUDICATION
from registration_data.models import RegistrationDataImport
from registration_datahub.tasks.deduplicate import DeduplicateTask
from sanction_list.tasks.check_against_sanction_list_pre_merge import CheckAgainstSanctionListPreMergeTask


class DeduplicateAndCheckAgainstSanctionsListTask:
    @transaction.atomic(using="default")
    def execute(self, should_populate_index, registration_data_import_id, individuals_ids):
        registration_data_import = (
            RegistrationDataImport.objects.get(id=registration_data_import_id) if registration_data_import_id else None
        )
        individuals = Individual.objects.filter(id__in=individuals_ids) if individuals_ids else None
        business_area = (
            registration_data_import.business_area if registration_data_import else individuals.first().business_area
        )

        if should_populate_index is True:
            populate_index(individuals, IndividualDocument)

        DeduplicateTask.deduplicate_individuals(
            registration_data_import=registration_data_import, individuals=individuals
        )
        ticket_details_to_create = []

        golden_record_duplicates = individuals.filter(deduplication_golden_record_status=DUPLICATE)

        ticket_details = create_needs_adjudication_tickets(
            golden_record_duplicates, "duplicates", business_area
        )
        ticket_details_to_create.extend(ticket_details)

        needs_adjudication = individuals.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)

        ticket_details = create_needs_adjudication_tickets(
            needs_adjudication, "possible_duplicates", business_area
        )
        ticket_details_to_create.extend(ticket_details)

        TicketNeedsAdjudicationDetails.objects.bulk_create(ticket_details_to_create)

        CheckAgainstSanctionListPreMergeTask.execute()
