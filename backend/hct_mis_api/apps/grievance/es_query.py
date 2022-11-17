import logging
from typing import Any, Dict, List

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.documents import GrievanceTicketDocument

logger = logging.getLogger(__name__)


TERM_FIELDS = (
    "category",
    "assigned_to",
    "issue_type",
    "priority",
    "urgency",
    "grievance_type",
    "registration_data_import",
)

OBJECT_FIELDS = (
    "admin2",
    "registration_data_import",
    "assigned_to",
)

TERMS_FIELDS = ("status", "admin2")


def execute_es_query(query_dict) -> List[str]:
    es_response = (
        GrievanceTicketDocument.search()
        .params(search_type="dfs_query_then_fetch", preserve_order=True)
        .from_dict(query_dict)
    )

    es_ids = [hit.meta.id for hit in es_response.scan()]
    return es_ids


def create_es_query(options) -> Dict:
    all_queries: List[Dict[str, Any]] = []
    query_search: List[Dict[str, Any]] = []
    query_term_fields: List[Dict[str, Any]] = []
    query_terms_fields: List[Dict[str, Any]] = []

    options["admin2"] = options.pop("admin", None)

    grievance_status = options.pop("grievance_status", "active")
    created_at_range = options.pop("created_at_range", None)

    business_area = options.pop("business_area")

    if created_at_range:
        date_range = {"range": {"created_at": {}}}

        min_date = created_at_range.pop("min", None)
        if min_date:
            date_range["range"]["created_at"]["gte"] = min_date.strftime("%Y-%m-%d")

        max_date = created_at_range.pop("max", None)
        if max_date:
            date_range["range"]["created_at"]["lte"] = max_date.strftime("%Y-%m-%d")
        all_queries.append(date_range)

    search = options.pop("search", None)
    if search and search.strip():
        key, value = tuple(search.split(" ", 1))
        if key == "ticket_id":
            query_search.append({"term": {"unicef_id": value}})
        elif key == "ticket_hh_id":
            query_search.append({"term": {"household_unicef_id": {"value": value}}})
        else:
            query_search.append({"term": {"ticket_details.household.head_of_household.family_name": {"value": value}}})

    order_by = options.pop("order_by", ["-created_at"])
    order_by = order_by[0]
    if order_by[0] == "-":
        sort = {order_by[1:]: {"order": "desc", "unmapped_type": "date"}}
    else:
        sort = {order_by: {"order": "asc", "unmapped_type": "date"}}

    for k, v in options.items():
        if k in TERM_FIELDS and v:
            if k in OBJECT_FIELDS:
                query_term_fields.append({"term": {f"{k}.id": {"value": decode_id_string(v)}}})
            else:
                query_term_fields.append({"term": {k: {"value": int(v) if v.isdigit() else v}}})

        if k in TERMS_FIELDS and v not in ([""], [None], None):
            if k == "admin2":
                query_terms_fields.append({"terms": {f"{k}.id": v}})
            else:
                query_terms_fields.append({"terms": {k: [int(status) for status in v]}})

    if grievance_status == "active" and options.get("status") == [""]:
        query_terms_fields.append({"terms": {"status": [1, 2, 3, 4, 5]}})

    all_queries.extend(query_term_fields)
    all_queries.extend(query_terms_fields)
    all_queries.extend(query_search)

    query_dict: Dict[str, Any] = {
        "query": {
            "bool": {
                "must": all_queries,
            }
        },
        "sort": [sort],
    }

    if business_area:
        query_dict["query"]["bool"]["filter"] = {"term": {"business_area.slug": business_area}}

    return query_dict
