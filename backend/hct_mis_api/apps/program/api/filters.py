from decimal import Decimal
from typing import Any

from django.db.models import DecimalField, Q, QuerySet
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from django_filters import rest_framework as filters

from hct_mis_api.apps.core.filters import DecimalRangeFilter
from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.program.models import ProgramCycle


class ProgramCycleFilter(filters.FilterSet):
    search = filters.CharFilter(method="search_filter")
    status = filters.MultipleChoiceFilter(
        choices=ProgramCycle.STATUS_CHOICE,
    )
    program = filters.CharFilter(method="filter_by_program")
    start_date = filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="end_date", lookup_expr="lte")
    total_delivered_quantity_usd = DecimalRangeFilter(method="filter_total_delivered_quantity_usd")

    class Meta:
        model = ProgramCycle
        fields = {
            "title": [
                "startswith",
            ],
        }

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_id=decode_id_string_required(value))

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(Q(title__istartswith=value) | Q(unicef_id__istartswith=value))
        return qs.filter(q_obj)

    def filter_total_delivered_quantity_usd(self, queryset: QuerySet, name: str, values: Any) -> QuerySet:
        min_value = values.get("min")
        max_value = values.get("max")
        q_obj = Q()
        if values:
            queryset = queryset.annotate(
                total_delivered_q_usd=Coalesce(
                    Sum("payment_plans__total_delivered_quantity_usd", output_field=DecimalField()), Decimal(0.0)
                )
            )
            if min_value is not None:
                q_obj &= Q(Q(total_delivered_q_usd__gte=min_value))
            if max_value is not None:
                q_obj &= Q(Q(total_delivered_q_usd__lte=max_value))
        return queryset.filter(q_obj)
