import re
import sys
from typing import Any, Dict, List, Optional

from hct_mis_api.apps.core.kobo.common import get_field_name


def get_record_model() -> Any:  # temp function
    from flags.state import flag_state

    if not bool(flag_state("NEW_RECORD_MODEL")):
        from hct_mis_api.apps.registration_datahub.models import Record
    else:
        from hct_mis_api.aurora.models import Record  # type: ignore[no-redef]

    return Record


def post_process_dedupe_results(record: Any) -> None:
    # TODO: record: ImportedIndividual but circular import
    max_score = 0
    min_score = sys.maxsize
    for field in [record.deduplication_batch_results, record.deduplication_golden_record_results]:
        if "duplicates" in field:
            duplicates = field["duplicates"]
            for entry in field["duplicates"]:
                max_score = max(max_score, entry["score"])
                min_score = min(min_score, entry["score"])
            field["score"] = {"max": max_score, "min": min_score, "qty": len(duplicates)}


def combine_collections(a: Dict, b: Dict, path: Optional[List] = None, update: bool = True) -> Dict:
    """merges b into a
    version from flex registration"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                combine_collections(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx in range(len(b[key])):
                    a[key][idx] = combine_collections(
                        a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update
                    )
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def find_attachment_in_kobo(attachments: List[Dict], value: str) -> Optional[Dict]:
    file_extension = value.split(".")[-1]
    filename = re.escape(".".join(value.split(".")[:-1]))
    regex_name = re.compile(f"{filename}(_\\w+)?\\.{file_extension}")
    for attachment in attachments:
        if regex_name.match(get_field_name(attachment["filename"])):
            return attachment
    return None
