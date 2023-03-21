from typing import Any, Dict

from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import Lower

from django_filters import CharFilter, DateFilter, FilterSet, MultipleChoiceFilter

from hct_mis_api.apps.core.filters import DecimalRangeFilter, IntegerRangeFilter
from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.program.models import Program


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=Program.STATUS_CHOICE)
    sector = MultipleChoiceFilter(field_name="sector", choices=Program.SECTOR_CHOICE)
    number_of_households = IntegerRangeFilter(method="filter_number_of_households")
    budget = DecimalRangeFilter(field_name="budget")
    start_date = DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        fields = (
            "business_area",
            "search",
            "status",
            "sector",
            "number_of_households",
            "budget",
            "start_date",
            "end_date",
        )
        model = Program

    order_by = CustomOrderingFilter(
        fields=(Lower("name"), "status", "start_date", "end_date", "sector", "total_number_of_households", "budget")
    )

    def filter_number_of_households(self, queryset: QuerySet, name: str, value: Dict) -> QuerySet:
        queryset = queryset.annotate(
            total_payment_plans_hh_count=Count(
                "cashplan__payment_items__household",
                filter=Q(cashplan__payment_items__delivered_quantity__gte=0),
                distinct=True,
            ),
            total_cash_plans_hh_count=Count(
                "paymentplan__payment_items__household",
                filter=Q(paymentplan__payment_items__delivered_quantity__gte=0),
                distinct=True,
            ),
        ).annotate(total_hh_count=F("total_payment_plans_hh_count") + F("total_cash_plans_hh_count"))

        if min_value := value.get("min"):
            queryset = queryset.filter(total_hh_count__gte=min_value)
        if max_value := value.get("max"):
            queryset = queryset.filter(total_hh_count__lte=max_value)

        return queryset

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__istartswith=value)
        return qs.filter(q_obj)


class ChartProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)

    class Meta:
        fields = ("business_area",)
        model = Program

    def search_filter(self, qs: QuerySet, name: str, value: Any) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)
