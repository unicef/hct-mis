from collections import defaultdict
from decimal import Decimal
<<<<<<< HEAD
from typing import Any, Dict, List, TypedDict
=======
from typing import Any, Dict, List
>>>>>>> origin

from django.db.models import DecimalField, F, Sum
from django.db.models.functions import Coalesce

<<<<<<< HEAD
=======
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
>>>>>>> origin
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentRecord


<<<<<<< HEAD
class QuantityType(TypedDict):
    total_delivered_quantity: Decimal
    currency: str


class ProgramType(TypedDict):
    id: str
    name: str
    quantity: List[QuantityType]


def programs_with_delivered_quantity(household: Household) -> List[Dict[str, Any]]:
=======
def programs_with_delivered_quantity(household: Household) -> List[Dict[str, Any]]:
    payment_items = ExtendedQuerySetSequence(household.paymentrecord_set.all(), household.payment_set.all())
>>>>>>> origin
    programs = (
        payment_items.select_related("parent__program")
        .exclude(status=PaymentRecord.STATUS_FORCE_FAILED)
        .values("parent__program")
        .order_by("parent__program")
        .annotate(
            total_delivered_quantity=Coalesce(Sum("delivered_quantity", output_field=DecimalField()), Decimal(0.0)),
            total_delivered_quantity_usd=Coalesce(
                Sum("delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
            ),
            program_name=F("parent__program__name"),
            currency=F("currency"),
            program_id=F("parent__program__id"),
            program_created_at=F("parent__program__created_at"),
        )
        .order_by("program_created_at")
        .merge_by(
            "parent__program",
            aggregated_fields=["total_delivered_quantity", "total_delivered_quantity_usd"],
            regular_fields=["program_name", "program_id", "program_created_at", "currency"],
        )
    )

    programs_dict: Dict[str, Dict] = defaultdict(dict)

    for program in programs:
        programs_dict[program["program_id"]]["id"] = encode_id_base64_required(program["program_id"], "Program")
        programs_dict[program["program_id"]]["name"] = program["program_name"]
        programs_dict[program["program_id"]]["quantity"] = programs_dict[program["program_id"]].get("quantity", [])

        programs_dict[program["program_id"]]["quantity"].append(
            {
                "total_delivered_quantity": program["total_delivered_quantity_usd"],
                "currency": "USD",
            }
        )

        if program["currency"] != "USD":
            programs_dict[program["program_id"]]["quantity"].append(
                {
                    "total_delivered_quantity": program["total_delivered_quantity"],
                    "currency": program["currency"],
                }
            )
<<<<<<< HEAD
=======

>>>>>>> origin
    return list(programs_dict.values())
