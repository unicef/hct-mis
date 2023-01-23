import enum
from datetime import datetime
from typing import Dict, Tuple, Type, Union

from django.core.files.uploadedfile import InMemoryUploadedFile

TYPE_ID = "ID"
TYPE_INTEGER = "INTEGER"
TYPE_STRING = "STRING"
TYPE_LIST_OF_IDS = "LIST_OF_IDS"
TYPE_BOOL = "BOOL"
TYPE_DATE = "DATE"
TYPE_IMAGE = "IMAGE"
TYPE_SELECT_ONE = "SELECT_ONE"
TYPE_SELECT_MANY = "SELECT_MANY"
TYPE_GEOPOINT = "GEOPOINT"
TYPE_DECIMAL = "DECIMAL"

FIELD_TYPES_TO_INTERNAL_TYPE: Dict[str, Union[Type, Tuple]] = {
    TYPE_ID: str,
    TYPE_INTEGER: int,
    TYPE_STRING: str,
    TYPE_LIST_OF_IDS: list,
    TYPE_BOOL: bool,
    TYPE_DATE: datetime,
    TYPE_IMAGE: (
        str,
        InMemoryUploadedFile,
    ),
    TYPE_SELECT_ONE: str,
    TYPE_SELECT_MANY: list,
    TYPE_GEOPOINT: str,
    TYPE_DECIMAL: str,
}

_INDIVIDUAL = "Individual"
_HOUSEHOLD = "Household"

FILTERABLE_TYPES = [TYPE_INTEGER, TYPE_STRING, TYPE_SELECT_ONE, TYPE_SELECT_MANY, TYPE_DATE, TYPE_BOOL]


class Scope(str, enum.Enum):
    KOBO_IMPORT = "KOBO_IMPORT"
    HOUSEHOLD_ID = "HOUSEHOLD_ID"
    COLLECTOR = "COLLECTOR"
    HOUSEHOLD_UPDATE = "HOUSEHOLD_UPDATE"
    INDIVIDUAL_UPDATE = "INDIVIDUAL_UPDATE"
    INDIVIDUAL_XLSX_UPDATE = "INDIVIDUAL_XLSX_UPDATE"
    TARGETING = "TARGETING"
    GLOBAL = "GLOBAL"
    XLSX = "XLSX"
