import logging

from constance import config
from django.utils import timezone

from grievance.models import TicketSystemFlaggingDetails, GrievanceTicket
from household.documents import IndividualDocument
from household.models import Individual, IDENTIFICATION_TYPE_NATIONAL_ID
from sanction_list.models import SanctionListIndividual

log = logging.getLogger(__name__)


class CheckAgainstSanctionListPreMergeTask:
    @staticmethod
    def _get_query_dict(individual):
        documents_numbers = [
            doc.document_number
            for doc in individual.documents.all()
            if doc.type_of_document.title() == "National Identification Number"
        ]
        query_dict = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "dis_max": {
                                "queries": [
                                    {"match": {"full_name": {"query": individual.full_name}}},
                                    {"terms": {"birth_date": [dob.date for dob in individual.dates_of_birth.all()]}},
                                    {"terms": {"documents.number": documents_numbers}},
                                    {
                                        "terms": {
                                            "documents.type": [
                                                IDENTIFICATION_TYPE_NATIONAL_ID for _ in documents_numbers
                                            ]
                                        }
                                    },
                                ]
                            }
                        }
                    ],
                }
            },
        }

        return query_dict

    @classmethod
    def execute(cls, individuals=None):
        if individuals is None:
            individuals = SanctionListIndividual.objects.all()
        possible_match_score = config.SANCTION_LIST_MATCH_SCORE
        document = IndividualDocument

        tickets_to_create = []
        ticket_details_to_create = []
        possible_matches = set()
        for individual in individuals:
            query_dict = cls._get_query_dict(individual)
            query = document.search().from_dict(query_dict)
            query._index = document._index._name

            results = query.execute()
            for individual_hit in results:
                score = individual_hit.meta.score
                if score >= possible_match_score:
                    marked_individual = Individual.objects.filter(individual_hit.id).first()
                    if marked_individual:
                        possible_matches.add(marked_individual.id)
                        ticket = GrievanceTicket(
                            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                            business_area=marked_individual.business_area,
                        )
                        ticket_details = TicketSystemFlaggingDetails(
                            ticket=ticket,
                            golden_records_individual=marked_individual,
                            sanction_list_individual=individual,
                        )
                        tickets_to_create.append(ticket)
                        ticket_details_to_create.append(ticket_details)

            log.debug(
                f"SANCTION LIST INDIVIDUAL: {individual.full_name} - reference number: {individual.reference_number}"
                f"Scores: ",
            )
            log.debug([(r.full_name, r.meta.score) for r in results])

        Individual.objects.filter(id__in=possible_matches).update(
            sanction_list_possible_match=True, sanction_list_last_check=timezone.now()
        )
        Individual.objects.exclude(id__in=possible_matches).update(
            sanction_list_possible_match=False, sanction_list_last_check=timezone.now()
        )

        GrievanceTicket.objects.bulk_create(tickets_to_create)
        TicketSystemFlaggingDetails.objects.bulk_create(ticket_details_to_create)
