import logging

from django.core.cache import cache
from django.utils import timezone

from constance import config

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.household.documents import IndividualDocument
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Individual,
)
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual

log = logging.getLogger(__name__)


class CheckAgainstSanctionListPreMergeTask:
    @staticmethod
    def _get_query_dict(individual):
        documents = [
            doc
            for doc in individual.documents.all()
            if doc.type_of_document.title() == "National Identification Number"
        ]
        document_queries = [
            {
                "bool": {
                    "must": [
                        {"match": {"documents.number": doc.document_number}},
                        {"match": {"documents.type": IDENTIFICATION_TYPE_NATIONAL_ID}},
                        {"match": {"documents.country": doc.issuing_country.alpha3}},
                    ],
                    "boost": 2,
                }
            }
            for doc in documents
        ]
        birth_dates_queries = [
            {"match": {"birth_date": {"query": dob.date, "boost": 1}}}
            for dob in individual.dates_of_birth.all()
        ]

        # alias_names_queries = [
        #     {
        #         "multi_match": {
        #             "query": alias_name.name,
        #             "fields": [
        #                 "full_name",
        #                 "first_name",
        #                 "middle_name",
        #                 "family_name",
        #             ],
        #             "boost": 1.3,
        #         }
        #     }
        #     for alias_name in individual.alias_names.all()
        # ]

        queries = [
            {
                "match": {
                    "full_name": {
                        "query": individual.full_name,
                        "boost": 4,
                        "operator": "and",
                    }
                }
            },
        ]
        queries.extend(document_queries)
        # queries.extend(alias_names_queries)
        queries.extend(birth_dates_queries)

        query_dict = {
            "size": 10000,
            "query": {
                "bool": {
                    "minimum_should_match": 1,
                    "should": queries,
                },
            },
        }

        return query_dict

    @classmethod
    def execute(cls, individuals=None, registration_data_import=None):
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
                    marked_individual = Individual.objects.filter(
                        id=individual_hit.id
                    ).first()
                    if marked_individual:
                        possible_matches.add(marked_individual.id)
                        household = marked_individual.household
                        admin_level_2 = household.admin2 if household else ""
                        admin_level_2_new = household.admin2_new if household else ""
                        area = household.village if household else ""
                        ticket = GrievanceTicket(
                            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                            business_area=marked_individual.business_area,
                            admin2=admin_level_2,
                            admin2_new=admin_level_2_new,
                            area=area,
                            registration_data_import=registration_data_import,
                        )
                        ticket_details = TicketSystemFlaggingDetails(
                            ticket=ticket,
                            golden_records_individual=marked_individual,
                            sanction_list_individual=individual,
                        )
                        details_already_exists = (
                            TicketSystemFlaggingDetails.objects.filter(
                                golden_records_individual=marked_individual,
                                sanction_list_individual=individual,
                            ).exists()
                        )
                        if details_already_exists is False:
                            tickets_to_create.append(ticket)
                            ticket_details_to_create.append(ticket_details)

            log.debug(
                f"SANCTION LIST INDIVIDUAL: {individual.full_name} - reference number: {individual.reference_number}"
                f" Scores: ",
            )
            log.debug([(r.full_name, r.meta.score) for r in results])
        cache.set("sanction_list_last_check", timezone.now(), None)
        Individual.objects.filter(
            id__in=possible_matches, sanction_list_possible_match=False
        ).update(sanction_list_possible_match=True)
        Individual.objects.exclude(id__in=possible_matches).filter(
            sanction_list_possible_match=True
        ).update(sanction_list_possible_match=False)

        GrievanceTicket.objects.bulk_create(tickets_to_create)
        for ticket in tickets_to_create:
            GrievanceNotification.send_all_notifications(
                GrievanceNotification.prepare_notification_for_ticket_creation(ticket)
            )
        TicketSystemFlaggingDetails.objects.bulk_create(ticket_details_to_create)
