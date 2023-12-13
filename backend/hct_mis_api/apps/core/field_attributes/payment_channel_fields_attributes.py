from hct_mis_api.apps.core.field_attributes.fields_types import (
    _INDIVIDUAL,
    TYPE_STRING,
    Scope,
)
from hct_mis_api.apps.core.field_attributes.lookup_functions import (
    get_debit_card_issuer,
    get_debit_card_number,
)

PAYMENT_CHANNEL_FIELDS_ATTRIBUTES = [
    {
        "id": "e5766962-1455-4ebc-8fad-fc89cdde792b",
        "type": TYPE_STRING,
        "name": "bank_name",
        "lookup": "bank_name",
        "required": False,
        "label": {"English(EN)": "Bank name"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "bank_name_i_c",
        "scope": [Scope.XLSX, Scope.PAYMENT_CHANNEL],
    },
    {
        "id": "3d6a45f3-d3f7-48a0-801b-7a98c0da517a",
        "type": TYPE_STRING,
        "name": "bank_account_number",
        "lookup": "bank_account_number",
        "required": False,
        "label": {"English(EN)": "Bank account number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "bank_account_number_i_c",
        "scope": [Scope.XLSX, Scope.PAYMENT_CHANNEL],
    },
    {
        "id": "72e79eec-0c10-42d9-9c25-86162232a389",
        "type": TYPE_STRING,
        "name": "debit_card_issuer",
        "lookup": "debit_card_issuer",
        "required": False,
        "label": {"English(EN)": "Debit Card Issuer"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "debit_card_issuer_i_c",
        "scope": [Scope.XLSX, Scope.PAYMENT_CHANNEL],
        "lookup_function": get_debit_card_issuer,
    },
    {
        "id": "4a2ae111-3450-41a4-8d26-5eb20f4e233c",
        "type": TYPE_STRING,
        "name": "debit_card_number",
        "lookup": "debit_card_number",
        "required": False,
        "label": {"English(EN)": "Debit card number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "debit_card_number_i_c",
        "scope": [Scope.XLSX, Scope.PAYMENT_CHANNEL],
        "lookup_function": get_debit_card_number,
    },
    {
        "id": "4a2ae111-3450-41a4-8d26-5eb20f4e233c",
        "type": TYPE_STRING,
        "name": "payment_delivery_phone_no",
        "lookup": "payment_delivery_phone_no",
        "required": False,
        "label": {"English(EN)": "Payment delivery phone number"},
        "hint": "",
        "choices": [],
        "associated_with": _INDIVIDUAL,
        "xlsx_field": "payment_delivery_phone_no_i_c",
        "scope": [Scope.XLSX, Scope.PAYMENT_CHANNEL, Scope.INDIVIDUAL_UPDATE, Scope.TARGETING],
    },
]
