from typing import List

from django.db import transaction

from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hct_mis_api.apps.household.documents import IndividualDocument
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    Document,
    Individual,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    CheckAgainstSanctionListPreMergeTask,
)
from hct_mis_api.apps.utils.elasticsearch_utils import populate_index


class DeduplicateAndCheckAgainstSanctionsListTask:
    @transaction.atomic(using="default")
    def execute(self, should_populate_index: bool, individuals_ids: List[str]):
        individuals = Individual.objects.filter(id__in=individuals_ids)
        business_area = individuals.first().business_area

        if should_populate_index is True:
            populate_index(individuals, IndividualDocument)

        DeduplicateTask.deduplicate_individuals_from_other_source(individuals, business_area)

        golden_record_duplicates = individuals.filter(deduplication_golden_record_status=DUPLICATE)

        create_needs_adjudication_tickets(golden_record_duplicates, "duplicates", business_area)

        needs_adjudication = individuals.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)

        create_needs_adjudication_tickets(needs_adjudication, "possible_duplicates", business_area)

        CheckAgainstSanctionListPreMergeTask.execute()
        DeduplicateTask.hard_deduplicate_documents(Document.objects.filter(individual_id__in=individuals_ids))
