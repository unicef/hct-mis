import graphene
from django.db.models import Case, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce, Lower
from django_filters import (
    CharFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
)
from graphene import ConnectionField, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    hopePermissionClass,
    Permissions,
)
from account.schema import LogEntryObjectConnection
from core.extended_connection import ExtendedConnection
from core.filters import DecimalRangeFilter, IntegerRangeFilter
from core.schema import ChoiceObject
from core.utils import to_choice_object, CustomOrderingFilter
from payment.models import CashPlanPaymentVerification, PaymentRecord
from program.models import CashPlan, Program


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=Program.STATUS_CHOICE)
    sector = MultipleChoiceFilter(field_name="sector", choices=Program.SECTOR_CHOICE)
    number_of_households = IntegerRangeFilter(field_name="households_count")
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
        fields=(Lower("name"), "status", "start_date", "end_date", "sector", "households_count", "budget")
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__icontains=value)
        return qs.filter(q_obj)


class ProgramNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
        ),
    )

    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    history = ConnectionField(LogEntryObjectConnection)
    individual_data_needed = graphene.Boolean()

    class Meta:
        model = Program
        filter_fields = [
            "name",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_history(self, info):
        return self.history.all()

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households


class CashPlanFilter(FilterSet):
    search = CharFilter(method="search_filter")
    delivery_type = MultipleChoiceFilter(field_name="delivery_type", choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    verification_status = MultipleChoiceFilter(
        field_name="verification_status", choices=CashPlanPaymentVerification.STATUS_CHOICES
    )

    class Meta:
        fields = {
            "program": ["exact"],
            "assistance_through": ["exact", "icontains"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
        }
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "ca_id",
            "status",
            "verification_status",
            "total_persons_covered",
            "total_delivered_quantity",
            "assistance_measurement",
            "assistance_through",
            "delivery_type",
            "start_date",
            "end_date",
            "program__name",
            "id",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__icontains=value)
            q_obj |= Q(ca_id__icontains=value)
        return qs.filter(q_obj)


class CashPlanNode(DjangoObjectType):
    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopePermissionClass(
                Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
            ),
        ),
    )
    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoFilterConnectionField(CashPlanNode, filterset_class=CashPlanFilter)
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)

    def resolve_all_programs(self, info, **kwargs):
        return (
            Program.objects.annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .annotate(households_count=Coalesce(Sum("cash_plans__total_persons_covered"), 0))
            .order_by("custom_order", "start_date")
        )

    def resolve_program_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_program_frequency_of_payments_choices(self, info, **kwargs):
        return to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE)

    def resolve_program_sector_choices(self, info, **kwargs):
        return to_choice_object(Program.SECTOR_CHOICE)

    def resolve_program_scope_choices(self, info, **kwargs):
        return to_choice_object(Program.SCOPE_CHOICE)

    def resolve_cash_plan_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_all_cash_plans(self, info, **kwargs):
        return CashPlan.objects.annotate(
            custom_order=Case(
                When(verification_status=CashPlanPaymentVerification.STATUS_ACTIVE, then=Value(1)),
                When(verification_status=CashPlanPaymentVerification.STATUS_PENDING, then=Value(2)),
                When(verification_status=CashPlanPaymentVerification.STATUS_FINISHED, then=Value(3)),
                output_field=IntegerField(),
            )
        ).order_by("-updated_at", "custom_order")
