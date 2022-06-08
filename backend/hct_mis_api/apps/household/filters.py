import json
import re

from constance import config
from django.db.models import Q
from django.db.models.functions import Lower

from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)

from hct_mis_api.apps.account.admin import BusinessAreaFilter
from hct_mis_api.apps.core.filters import (
    AgeRangeFilter,
    DateRangeFilter,
    IntegerRangeFilter,
    BusinessAreaSlugFilter,
)
from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.documents import IndividualDocument, HouseholdDocument
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    NEEDS_ADJUDICATION,
    SANCTION_LIST_CONFIRMED_MATCH,
    SANCTION_LIST_POSSIBLE_MATCH,
    SEX_CHOICE,
    STATUS_ACTIVE,
    STATUS_DUPLICATE,
    STATUS_WITHDRAWN,
    Household,
    Individual,
)
from hct_mis_api.apps.program.models import Program


class HouseholdFilter(FilterSet):
    business_area = BusinessAreaSlugFilter()
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")
    head_of_household__full_name = CharFilter(field_name="head_of_household__full_name", lookup_expr="startswith")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(
        field_name="admin_area_new", queryset=Area.objects.filter(area_type__area_level=2)
    )
    withdrawn = BooleanFilter(field_name="withdrawn")

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact"],
            "country_origin": ["exact", "startswith"],
            "address": ["exact", "startswith"],
            "head_of_household__full_name": ["exact", "startswith"],
            "size": ["range", "lte", "gte"],
            "admin_area_new": ["exact"],
            "target_populations": ["exact"],
            "programs": ["exact"],
            "residence_status": ["exact"],
            "withdrawn": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "age",
            "sex",
            "household__id",
            "id",
            "unicef_id",
            "household_ca_id",
            "size",
            Lower("head_of_household__full_name"),
            Lower("admin_area_new__name"),
            "residence_status",
            Lower("registration_data_import__name"),
            "total_cash_received",
            "last_registration_date",
            "first_registration_date",
        )
    )

    def _search_es(self, qs, value):
        query_dict = get_elasticsearch_query_for_households(value)
        es_response = (
            HouseholdDocument.search().params(search_type="dfs_query_then_fetch").from_dict(query_dict).execute()
        )
        es_ids = [x.meta["id"] for x in es_response]
        return qs.filter(Q(id__in=es_ids)).distinct()

    def search_filter(self, qs, name, value):
        if config.USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH:
            return self._search_es(qs, value)
        return self._search_db(qs, value)

    def _search_db(self, qs, value):
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            inner_query = Q()
            inner_query |= Q(head_of_household__full_name__istartswith=value)
            inner_query |= Q(head_of_household__given_name__istartswith=value)
            inner_query |= Q(head_of_household__middle_name__istartswith=value)
            inner_query |= Q(head_of_household__family_name__istartswith=value)
            inner_query |= Q(residence_status__istartswith=value)
            inner_query |= Q(admin_area__title__istartswith=value)
            inner_query |= Q(admin_area_new__name__istartswith=value)
            inner_query |= Q(unicef_id__istartswith=value)
            inner_query |= Q(unicef_id__iendswith=value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()


class IndividualFilter(FilterSet):
    business_area = BusinessAreaSlugFilter()
    age = AgeRangeFilter(field_name="birth_date")
    sex = MultipleChoiceFilter(field_name="sex", choices=SEX_CHOICE)
    programs = ModelMultipleChoiceFilter(field_name="household__programs", queryset=Program.objects.all())
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(
        field_name="household__admin_area_new", queryset=Area.objects.filter(area_type__area_level=2)
    )
    status = MultipleChoiceFilter(choices=INDIVIDUAL_STATUS_CHOICES, method="status_filter")
    excluded_id = CharFilter(method="filter_excluded_id")
    withdrawn = BooleanFilter(field_name="withdrawn")
    flags = MultipleChoiceFilter(choices=INDIVIDUAL_FLAGS_CHOICES, method="flags_filter")

    class Meta:
        model = Individual
        fields = {
            "household__id": ["exact"],
            "business_area": ["exact"],
            "full_name": ["exact", "startswith", "endswith"],
            "sex": ["exact"],
            "household__admin_area": ["exact"],
            "household__admin_area_new": ["exact"],
            "withdrawn": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            "unicef_id",
            Lower("full_name"),
            "household__id",
            "household__unicef_id",
            "birth_date",
            "sex",
            "relationship",
            Lower("household__admin_area_new__name"),
            "last_registration_date",
            "first_registration_date",
        )
    )

    def flags_filter(self, qs, name, value):
        q_obj = Q()
        if NEEDS_ADJUDICATION in value:
            q_obj |= Q(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        if DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if SANCTION_LIST_POSSIBLE_MATCH in value:
            q_obj |= Q(sanction_list_possible_match=True, sanction_list_confirmed_match=False)
        if SANCTION_LIST_CONFIRMED_MATCH in value:
            q_obj |= Q(sanction_list_confirmed_match=True)

        return qs.filter(q_obj)

    def _search_es(self, qs, value):
        query_dict = get_elasticsearch_query_for_individuals(value)
        es_response = (
            IndividualDocument.search().params(search_type="dfs_query_then_fetch").from_dict(query_dict).execute()
        )
        es_ids = [x.meta["id"] for x in es_response]
        return qs.filter(Q(id__in=es_ids)).distinct()

    def search_filter(self, qs, name, value):
        if config.USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH:
            return self._search_es(qs, value)
        return self._search_db(qs, value)

    def _search_db(self, qs, value):
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            inner_query = Q(household__admin_area__title__istartswith=value)
            inner_query |= Q(household__admin_area_new__name__istartswith=value)
            inner_query |= Q(unicef_id__istartswith=value)
            inner_query |= Q(unicef_id__iendswith=value)
            inner_query |= Q(household__unicef_id__istartswith=value)
            inner_query |= Q(full_name__istartswith=value)
            inner_query |= Q(given_name__istartswith=value)
            inner_query |= Q(middle_name__istartswith=value)
            inner_query |= Q(family_name__istartswith=value)
            inner_query |= Q(documents__document_number__istartswith=value)
            inner_query |= Q(phone_no__istartswith=value)
            inner_query |= Q(phone_no_alternative__istartswith=value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()

    def status_filter(self, qs, name, value):
        q_obj = Q()
        if STATUS_DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if STATUS_WITHDRAWN in value:
            q_obj |= Q(withdrawn=True)
        if STATUS_ACTIVE in value:
            q_obj |= Q(duplicate=False, withdrawn=False)

        return qs.filter(q_obj).distinct()

    def filter_excluded_id(self, qs, name, value):
        return qs.exclude(id=decode_id_string(value))


def get_elasticsearch_query_for_individuals(value):
    match_fields = [
        "phone_no_text",
        "phone_no_alternative",
        "documents.number",
        "admin1",
        "admin2",
    ]
    prefix_fields = [
        # "full_name",
        "middle_name",
        "unicef_id",
        "household.unicef_id",
        "phone_no_text"
    ]
    wildcard_fields = ["phone_no", "unicef_id", "household.unicef_id"]
    match_queries = [
        {
            "match": {
                x: {
                    "query": value,
                }
            }
        }
        for x in match_fields
    ]
    prefix_queries = [
        {
            "match_phrase_prefix": {
                x: {
                    "query": value,
                }
            }
        }
        for x in prefix_fields
    ]
    wildcard_queries = [
        {
            "wildcard": {
                x: {
                    "value": f"*{value}",
                }
            }
        }
        for x in wildcard_fields
    ]
    all_queries = []
    all_queries.extend(wildcard_queries)
    all_queries.extend(prefix_queries)
    all_queries.extend(match_queries)

    values = value.split(" ")
    if len(values) == 2:
        all_queries.extend(
            [
                {
                    "match_phrase_prefix": {
                        "given_name": {
                            "query": values[0],
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "family_name": {
                            "query": values[1],
                        }
                    }
                },
            ]
        )
    else:
        all_queries.extend(
            [
                {
                    "match_phrase_prefix": {
                        "given_name": {
                            "query": value,
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "family_name": {
                            "query": value,
                        }
                    }
                },
            ]
        )


    query = {
        "size": "100",
        "_source": False,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
    }
    return query


def get_elasticsearch_query_for_households(value):
    match_fields = [
        "admin1",
        "admin2",
    ]
    prefix_fields = ["head_of_household.middle_name", "unicef_id", "residence_status"]
    wildcard_fields = ["unicef_id"]
    match_queries = [
        {
            "match": {
                x: {
                    "query": value,
                }
            }
        }
        for x in match_fields
    ]
    prefix_queries = [
        {
            "match_phrase_prefix": {
                x: {
                    "query": value,
                }
            }
        }
        for x in prefix_fields
    ]
    wildcard_queries = [
        {
            "wildcard": {
                x: {
                    "value": f"*{value}",
                }
            }
        }
        for x in wildcard_fields
    ]
    all_queries = []
    all_queries.extend(wildcard_queries)
    all_queries.extend(prefix_queries)
    all_queries.extend(match_queries)

    values = value.split(" ")
    if len(values) == 2:
        all_queries.extend(
            [
                {
                    "match_phrase_prefix": {
                        "head_of_household.given_name": {
                            "query": values[0],
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "head_of_household.family_name": {
                            "query": values[1],
                        }
                    }
                },
            ]
        )
    else:
        all_queries.extend(
            [
                {
                    "match_phrase_prefix": {
                        "head_of_household.given_name": {
                            "query": value,
                        }
                    }
                },
                {
                    "match_phrase_prefix": {
                        "head_of_household.family_name": {
                            "query": value,
                        }
                    }
                },
            ]
        )

    query = {
        "size": "100",
        "_source": False,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
    }
    print(json.dumps(query))
    return query
