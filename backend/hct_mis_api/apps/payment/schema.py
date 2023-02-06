import json
from base64 import b64decode
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Union

from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Case,
    CharField,
    Count,
    Exists,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

import _decimal
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay import to_global_id
from graphql_relay.connection.arrayconnection import connection_from_list_slice

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    DjangoPermissionFilterFastConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.schema import LogEntryNode
from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    chart_create_filter_query_for_payment_verification_gfk,
    chart_filters_decoder,
    chart_get_filtered_qs,
    chart_map_choices,
    chart_permission_decorator,
    decode_id_string,
    encode_id_base64,
    to_choice_object,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import STATUS_ACTIVE, STATUS_INACTIVE
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.payment.filters import (
    FinancialServiceProviderFilter,
    FinancialServiceProviderXlsxReportFilter,
    FinancialServiceProviderXlsxTemplateFilter,
    PaymentFilter,
    PaymentPlanFilter,
    PaymentRecordFilter,
    PaymentVerificationFilter,
    PaymentVerificationLogEntryFilter,
    PaymentVerificationPlanFilter,
    cash_plan_and_payment_plan_filter,
    cash_plan_and_payment_plan_ordering,
)
from hct_mis_api.apps.payment.inputs import GetCashplanVerificationSampleSizeInput
from hct_mis_api.apps.payment.managers import ArraySubquery
from hct_mis_api.apps.payment.models import (
    Approval,
    ApprovalProcess,
    CashPlan,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    FinancialServiceProviderXlsxTemplate,
    GenericPayment,
    Payment,
    PaymentChannel,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.services.sampling import Sampling
from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
    does_payment_record_have_right_hoh_phone_number,
)
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.targeting.graphql_types import TargetPopulationNode
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    SectionTotalNode,
    TableTotalCashTransferred,
)


class RapidProFlowResult(graphene.ObjectType):
    key = graphene.String()
    name = graphene.String()
    categories = graphene.List(graphene.String)
    node_uuids = graphene.List(graphene.String)


class RapidProFlowRun(graphene.ObjectType):
    active = graphene.Int()
    completed = graphene.Int()
    interrupted = graphene.Int()
    expired = graphene.Int()


class RapidProFlow(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    type = graphene.String()
    archived = graphene.Boolean()
    labels = graphene.List(graphene.String)
    expires = graphene.Int()
    runs = graphene.List(RapidProFlowRun)
    results = graphene.List(RapidProFlowResult)
    # parent_refs
    created_on = graphene.DateTime()
    modified_on = graphene.DateTime()

    def resolve_id(parent, info: Any) -> str:
        return parent["uuid"]  # type: ignore # FIXME


class FinancialServiceProviderXlsxTemplateNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.FINANCIAL_SERVICE_PROVIDER_XLSX_TEMPLATE_VIEW_LIST_AND_DETAILS),
    )

    class Meta:
        model = FinancialServiceProviderXlsxTemplate
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FinancialServiceProviderXlsxReportNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.FINANCIAL_SERVICE_PROVIDER_VIEW_LIST_AND_DETAILS),)

    class Meta:
        model = FinancialServiceProviderXlsxReport
        exclude = ("file",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    report_url = graphene.String()

    def resolve_report_url(self, info: Any, **kwargs: Any) -> graphene.String:
        return self.file.url if self.file else ""


class FinancialServiceProviderNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.FINANCIAL_SERVICE_PROVIDER_VIEW_LIST_AND_DETAILS),)
    full_name = graphene.String(source="name")

    class Meta:
        model = FinancialServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ServiceProviderNode(DjangoObjectType):
    class Meta:
        model = ServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AgeFilterObject(graphene.ObjectType):
    min = graphene.Int()
    max = graphene.Int()


class PaymentVerificationSummaryNode(DjangoObjectType):
    class Meta:
        model = PaymentVerificationSummary
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class GetCashplanVerificationSampleSizeObject(graphene.ObjectType):
    payment_record_count = graphene.Int()
    sample_size = graphene.Int()


class ChartPaymentVerification(ChartDetailedDatasetsNode):
    households = graphene.Int()
    average_sample_size = graphene.Float()


class ApprovalNode(DjangoObjectType):
    info = graphene.String()

    class Meta:
        model = Approval
        fields = ("created_at", "comment", "info", "created_by")

    def resolve_info(self, info: Any) -> graphene.String:
        return self.info


class FilteredActionsListNode(graphene.ObjectType):
    approval = graphene.List(ApprovalNode)
    authorization = graphene.List(ApprovalNode)
    finance_review = graphene.List(ApprovalNode)
    reject = graphene.List(ApprovalNode)


class ApprovalProcessNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_DETAILS),)
    rejected_on = graphene.String()
    actions = graphene.Field(FilteredActionsListNode)

    class Meta:
        model = ApprovalProcess
        exclude = ("approvals",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_rejected_on(self, info: Any) -> Optional[str]:
        if self.approvals.filter(type=Approval.REJECT).exists():
            if self.sent_for_finance_review_date:
                return "IN_REVIEW"
            if self.sent_for_authorization_date:
                return "IN_AUTHORIZATION"
            if self.sent_for_approval_date:
                return "IN_APPROVAL"
        return None

    def resolve_actions(self, info: Any) -> "FilteredActionsListNode":
        resp = FilteredActionsListNode(
            approval=self.approvals.filter(type=Approval.APPROVAL),
            authorization=self.approvals.filter(type=Approval.AUTHORIZATION),
            finance_review=self.approvals.filter(type=Approval.FINANCE_REVIEW),
            reject=self.approvals.filter(type=Approval.REJECT),
        )
        return resp


class PaymentConflictDataNode(graphene.ObjectType):
    payment_plan_id = graphene.String()
    payment_plan_unicef_id = graphene.String()
    payment_plan_start_date = graphene.String()
    payment_plan_end_date = graphene.String()
    payment_plan_status = graphene.String()
    payment_id = graphene.String()
    payment_unicef_id = graphene.String()

    def resolve_payment_plan_id(self, info: Any) -> Optional[str]:
        return encode_id_base64(self["payment_plan_id"], "PaymentPlan")  # type: ignore

    def resolve_payment_id(self, info: Any) -> Optional[str]:
        return encode_id_base64(self["payment_id"], "Payment")  # type: ignore


class GenericPaymentNode(graphene.ObjectType):
    """using this for GenericFK like in PaymentVerification (Payment and PaymentRecord models)"""

    id = graphene.String()
    obj_type = graphene.String()
    unicef_id = graphene.String()
    currency = graphene.String()
    delivered_quantity = graphene.Float()
    delivered_quantity_usd = graphene.Float()
    household = graphene.Field(HouseholdNode)

    def resolve_id(self, info: Any) -> str:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any) -> str:
        return self.__class__.__name__

    def resolve_unicef_id(self, info: Any) -> graphene.String:
        return self.unicef_id

    def resolve_currency(self, info: Any) -> graphene.String:
        return self.currency

    def resolve_delivered_quantity_usd(self, info: Any) -> graphene.Float:
        return self.delivered_quantity_usd

    def resolve_delivered_quantity(self, info: Any) -> graphene.Float:
        return self.delivered_quantity

    def resolve_household(self, info: Any) -> graphene.Field:
        return self.household


class PaymentNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_DETAILS),)
    payment_plan_hard_conflicted = graphene.Boolean()
    payment_plan_hard_conflicted_data = graphene.List(PaymentConflictDataNode)
    payment_plan_soft_conflicted = graphene.Boolean()
    payment_plan_soft_conflicted_data = graphene.List(PaymentConflictDataNode)
    has_payment_channel = graphene.Boolean()
    full_name = graphene.String()
    target_population = graphene.Field(TargetPopulationNode)
    verification = graphene.Field("hct_mis_api.apps.payment.schema.PaymentVerificationNode")
    distribution_modality = graphene.String()
    total_persons_covered = graphene.Int()
    service_provider = graphene.Field(FinancialServiceProviderNode)

    class Meta:
        model = Payment
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment_plan_hard_conflicted_data(self, info: Any) -> List[Any]:
        if self.parent.status != PaymentPlan.Status.OPEN:
            return list()
        return PaymentNode._parse_pp_conflict_data(getattr(self, "payment_plan_hard_conflicted_data", []))

    def resolve_payment_plan_soft_conflicted_data(self, info: Any) -> List[Any]:
        if self.parent.status != PaymentPlan.Status.OPEN:
            return list()
        return PaymentNode._parse_pp_conflict_data(getattr(self, "payment_plan_soft_conflicted_data", []))

    def resolve_has_payment_channel(self, info: Any) -> bool:
        return self.collector.payment_channels.exists()

    def resolve_payment_plan_hard_conflicted(self, info: Any) -> Union[Any, graphene.Boolean]:
        return self.parent.status == PaymentPlan.Status.OPEN and self.payment_plan_hard_conflicted

    def resolve_payment_plan_soft_conflicted(self, info: Any) -> Union[Any, graphene.Boolean]:
        return self.parent.status == PaymentPlan.Status.OPEN and self.payment_plan_soft_conflicted

    def resolve_target_population(self, info: Any) -> TargetPopulation:
        return self.parent.target_population

    def resolve_full_name(self, info: Any) -> str:
        return self.head_of_household.full_name if self.head_of_household else ""

    def resolve_verification(self, info: Any) -> graphene.Field:
        return self.verification

    def resolve_distribution_modality(self, info: Any) -> str:
        return self.parent.unicef_id

    def resolve_total_persons_covered(self, info: Any) -> Optional[int]:
        # TODO: in feature will get data from snap shot
        return self.household.size

    def resolve_service_provider(self, info: Any) -> Optional[FinancialServiceProvider]:
        return self.financial_service_provider

    @classmethod
    def _parse_pp_conflict_data(cls, conflicts_data: List) -> List[Any]:
        """parse list of conflicted payment plans data from Payment model json annotations"""
        return [json.loads(conflict) for conflict in conflicts_data]


class DeliveryMechanismNode(DjangoObjectType):
    name = graphene.String()
    order = graphene.Int()
    fsp = graphene.Field(FinancialServiceProviderNode)

    def resolve_name(self, info: Any) -> graphene.String:
        return self.delivery_mechanism

    def resolve_order(self, info: Any) -> graphene.Int:
        return self.delivery_mechanism_order

    def resolve_fsp(self, info: Any) -> graphene.Field:
        return self.financial_service_provider

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


def _calculate_volume(
    delivery_mechanism_per_payment_plan: "DeliveryMechanismPerPaymentPlan", field: str
) -> Optional[Decimal]:
    if not delivery_mechanism_per_payment_plan.financial_service_provider:
        return None
    payments = delivery_mechanism_per_payment_plan.payment_plan.not_excluded_payments.filter(
        financial_service_provider=delivery_mechanism_per_payment_plan.financial_service_provider,
        assigned_payment_channel__delivery_mechanism__delivery_mechanism=delivery_mechanism_per_payment_plan.delivery_mechanism,
    )
    return payments.aggregate(entitlement_sum=Coalesce(Sum(field), Decimal(0.0)))["entitlement_sum"]


class VolumeByDeliveryMechanismNode(graphene.ObjectType):
    delivery_mechanism = graphene.Field(DeliveryMechanismNode)
    volume = graphene.Float()
    volume_usd = graphene.Float()

    def resolve_delivery_mechanism(self, info: Any) -> "VolumeByDeliveryMechanismNode":
        return self  # DeliveryMechanismNode uses the same model

    def resolve_volume(self, info: Any) -> Optional[_decimal.Decimal]:  # non-usd
        return _calculate_volume(self, "entitlement_quantity")  # type: ignore

    def resolve_volume_usd(self, info: Any) -> Optional[_decimal.Decimal]:
        return _calculate_volume(self, "entitlement_quantity_usd")  # type: ignore

    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FspChoices(graphene.ObjectType):
    class FspChoice(graphene.ObjectType):
        id = graphene.String()
        name = graphene.String()

        def resolve_id(self, info: Any) -> Optional[str]:
            return encode_id_base64(self["id"], "FinancialServiceProvider")  # type: ignore

    delivery_mechanism = graphene.String()
    fsps = graphene.List(FspChoice)


class PaymentPlanNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_DETAILS),)
    approval_number_required = graphene.Int()
    authorization_number_required = graphene.Int()
    finance_review_number_required = graphene.Int()
    dispersion_start_date = graphene.Date()
    dispersion_end_date = graphene.Date()
    start_date = graphene.Date()
    end_date = graphene.Date()
    currency_name = graphene.String()
    has_payment_list_export_file = graphene.Boolean()
    imported_file_name = graphene.String()
    payments_conflicts_count = graphene.Int()
    delivery_mechanisms = graphene.List(DeliveryMechanismNode)
    volume_by_delivery_mechanism = graphene.List(VolumeByDeliveryMechanismNode)
    verification_plans = DjangoPermissionFilterConnectionField(
        "hct_mis_api.apps.program.schema.PaymentVerificationPlanNode",  # type: ignore
        filterset_class=PaymentVerificationPlanFilter,
    )
    payment_verification_summary = graphene.Field(
        PaymentVerificationSummaryNode,
        source="get_payment_verification_summary",
    )
    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    can_create_payment_verification_plan = graphene.Boolean()
    available_payment_records_count = graphene.Int()

    class Meta:
        model = PaymentPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_verification_plans(self, info: Any) -> graphene.List:
        return self.get_payment_verification_plans

    def resolve_approval_number_required(self, info: Any) -> graphene.Int:
        return self.business_area.approval_number_required

    def resolve_authorization_number_required(self, info: Any) -> graphene.Int:
        return self.business_area.authorization_number_required

    def resolve_finance_review_number_required(self, info: Any) -> graphene.Int:
        return self.business_area.finance_review_number_required

    def resolve_payments_conflicts_count(self, info: Any) -> graphene.Int:
        return self.payment_items.filter(payment_plan_hard_conflicted=True).count()

    def resolve_currency_name(self, info: Any) -> graphene.String:
        return self.get_currency_display()

    def resolve_delivery_mechanisms(self, info: Any) -> graphene.List:
        return DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=self).order_by("delivery_mechanism_order")

    def resolve_has_payment_list_export_file(self, info: Any) -> graphene.Boolean:
        return self.has_export_file

    def resolve_imported_file_name(self, info: Any) -> graphene.String:
        return self.imported_file.file.name if self.imported_file else ""

    def resolve_volume_by_delivery_mechanism(self, info: Any) -> graphene.List:
        return DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=self).order_by("delivery_mechanism_order")

    def resolve_available_payment_records_count(self, info: Any, **kwargs: Any) -> graphene.Int:
        return self.payment_items.filter(status__in=Payment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0).count()


class PaymentVerificationNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS),)
    is_manually_editable = graphene.Boolean()
    payment = graphene.Field(GenericPaymentNode)

    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment(self, info: Any) -> graphene.Field:
        return self.get_payment


class PaymentVerificationPlanNode(DjangoObjectType):
    excluded_admin_areas_filter = graphene.List(graphene.String)
    age_filter = graphene.Field(AgeFilterObject)
    xlsx_file_was_downloaded = graphene.Boolean()
    has_xlsx_file = graphene.Boolean()
    payment_plan = graphene.Field(PaymentPlanNode)

    class Meta:
        model = PaymentVerificationPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_xlsx_file_was_downloaded(self, info: Any) -> bool:
        return self.xlsx_payment_verification_plan_file_was_downloaded

    def resolve_has_xlsx_file(self, info: Any) -> bool:
        return self.has_xlsx_payment_verification_plan_file


class PaymentRecordNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS),)
    verification = graphene.Field(PaymentVerificationNode)
    unicef_id = graphene.String(source="ca_id")

    class Meta:
        model = PaymentRecord
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentVerificationLogEntryNode(LogEntryNode):
    content_object = graphene.Field(PaymentVerificationPlanNode)

    class Meta:
        model = LogEntry
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class PaymentChannelNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_DETAILS),)

    class Meta:
        model = PaymentChannel
        exclude = ("delivery_data",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AvailableFspsForDeliveryMechanismsInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)


class CashPlanAndPaymentPlanNode(BaseNodePermissionMixin, graphene.ObjectType):
    """
    for CashPlan and PaymentPlan models
    """

    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    )

    obj_type = graphene.String()
    id = graphene.String()
    unicef_id = graphene.String(source="get_unicef_id")
    verification_status = graphene.String()
    currency = graphene.String()
    total_delivered_quantity = graphene.Float()
    start_date = graphene.String()
    end_date = graphene.String()
    programme_name = graphene.String()
    updated_at = graphene.String()
    verification_plans = graphene.List(PaymentVerificationPlanNode)
    total_number_of_households = graphene.Int()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()

    # TODO: Fields with dummy data
    assistance_measurement = graphene.String()
    dispersion_date = graphene.String()
    service_provider_full_name = graphene.String()

    def resolve_id(self, info: Any, **kwargs: Any) -> str:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any, **kwargs: Any) -> str:
        return self.__class__.__name__

    def resolve_verification_status(self, info: Any, **kwargs: Any) -> Optional[graphene.String]:
        return self.get_payment_verification_summary.status if self.get_payment_verification_summary else None

    def resolve_programme_name(self, info: Any, **kwargs: Any) -> graphene.String:
        return self.program.name

    def resolve_verification_plans(self, info: Any, **kwargs: Any) -> graphene.List:
        return self.payment_verification_plan.all()

    # TODO: do we need this empty fields ??
    def resolve_assistance_measurement(self, info: Any, **kwargs: Any) -> str:
        return "HH"

    def resolve_dispersion_date(self, info: Any, **kwargs: Any) -> str:
        return ""

    def resolve_service_provider_full_name(self, info: Any, **kwargs: Any) -> str:
        return ""


class PageInfoNode(graphene.ObjectType):
    start_cursor = graphene.String()
    end_cursor = graphene.String()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()


class CashPlanAndPaymentPlanEdges(graphene.ObjectType):
    cursor = graphene.String()
    node = graphene.Field(CashPlanAndPaymentPlanNode)


class PaginatedCashPlanAndPaymentPlanNode(graphene.ObjectType):
    page_info = graphene.Field(PageInfoNode)
    edges = graphene.List(CashPlanAndPaymentPlanEdges)
    total_count = graphene.Int()


class GenericPaymentPlanNode(graphene.ObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    )

    id = graphene.String()
    obj_type = graphene.String()
    payment_verification_summary = graphene.Field(PaymentVerificationSummaryNode)
    available_payment_records_count = graphene.Int()
    verification_plans = DjangoPermissionFilterConnectionField(
        PaymentVerificationPlanNode,
        filterset_class=PaymentVerificationPlanFilter,
    )
    status_date = graphene.DateTime()
    status = graphene.String()

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    delivery_type = graphene.String()
    total_number_of_households = graphene.Int()
    currency = graphene.String(source="currency")
    total_delivered_quantity = graphene.Float()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()
    can_create_payment_verification_plan = graphene.Boolean()

    def resolve_id(self, info: Any, **kwargs: Any) -> graphene.String:
        return to_global_id(self.__class__.__name__ + "Node", self.id)

    def resolve_obj_type(self, info: Any, **kwargs: Any) -> str:
        return self.__class__.__name__

    def resolve_payment_verification_summary(self, info: Any, **kwargs: Any) -> graphene.Field:
        return self.get_payment_verification_summary

    def resolve_available_payment_records_count(self, info: Any, **kwargs: Any) -> graphene.Int:
        return self.payment_items.filter(
            status__in=PaymentRecord.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    def resolve_verification_plans(self, info: Any, **kwargs: Any) -> DjangoPermissionFilterConnectionField:
        return self.get_payment_verification_plans

    def resolve_total_entitled_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_entitled_quantity

    def resolve_total_delivered_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_delivered_quantity

    def resolve_total_undelivered_quantity(self, info: Any, **kwargs: Any) -> graphene.Float:
        return self.total_undelivered_quantity

    def resolve_can_create_payment_verification_plan(self, info: Any, **kwargs: Any) -> graphene.Boolean:
        return self.can_create_payment_verification_plan

    def resolve_status_date(self, info: Any, **kwargs: Any) -> graphene.DateTime:
        return self.status_date

    def resolve_status(self, info: Any, **kwargs: Any) -> graphene.String:
        return self.status


class Query(graphene.ObjectType):
    payment = relay.Node.Field(PaymentNode)
    all_payments = DjangoPermissionFilterConnectionField(
        PaymentNode,
        filterset_class=PaymentFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_LIST),),
    )
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoPermissionFilterConnectionField(
        PaymentRecordNode,
        filterset_class=PaymentRecordFilter,
        permission_classes=(hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),),
    )

    financial_service_provider_xlsx_template = relay.Node.Field(FinancialServiceProviderXlsxTemplateNode)
    all_financial_service_provider_xlsx_templates = DjangoPermissionFilterConnectionField(
        FinancialServiceProviderXlsxTemplateNode,
        filterset_class=FinancialServiceProviderXlsxTemplateFilter,
    )

    financial_service_provider_xlsx_report = relay.Node.Field(FinancialServiceProviderXlsxReportNode)
    all_financial_service_provider_xlsx_reports = DjangoPermissionFilterConnectionField(
        FinancialServiceProviderXlsxReportNode,
        filterset_class=FinancialServiceProviderXlsxReportFilter,
    )

    financial_service_provider = relay.Node.Field(FinancialServiceProviderNode)
    all_financial_service_providers = DjangoPermissionFilterConnectionField(
        FinancialServiceProviderNode,
        filterset_class=FinancialServiceProviderFilter,
    )

    payment_record_verification = relay.Node.Field(PaymentVerificationNode)
    all_payment_verifications = DjangoPermissionFilterConnectionField(
        PaymentVerificationNode,
        filterset_class=PaymentVerificationFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )

    payment_verification_plan = relay.Node.Field(PaymentVerificationPlanNode)
    all_payment_verification_plan = DjangoPermissionFilterConnectionField(
        PaymentVerificationPlanNode,
        filterset_class=PaymentVerificationPlanFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),),
    )

    chart_payment_verification = graphene.Field(
        ChartPaymentVerification,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_volume_by_delivery_mechanism = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_payment = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_total_transferred = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    table_total_cash_transferred_by_administrative_area = graphene.Field(
        TableTotalCashTransferred,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
        order=graphene.String(required=False),
        order_by=graphene.String(required=False),
    )
    chart_total_transferred_cash_by_country = graphene.Field(
        ChartDetailedDatasetsNode, year=graphene.Int(required=True)
    )

    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_channel_choices = graphene.List(ChoiceObject)
    payment_verification_status_choices = graphene.List(ChoiceObject)

    all_rapid_pro_flows = graphene.List(
        RapidProFlow,
        business_area_slug=graphene.String(required=True),
    )
    sample_size = graphene.Field(
        GetCashplanVerificationSampleSizeObject,
        input=GetCashplanVerificationSampleSizeInput(),
    )

    all_payment_verification_log_entries = DjangoPermissionFilterFastConnectionField(
        PaymentVerificationLogEntryNode,
        filterset_class=PaymentVerificationLogEntryFilter,
        permission_classes=(hopePermissionClass(Permissions.ACTIVITY_LOG_VIEW),),
    )

    payment_plan = relay.Node.Field(PaymentPlanNode)
    # TODO: Keep or remove??? in favour of all_cash_plans_and_payment_plans
    all_payment_plans = DjangoPermissionFilterConnectionField(
        PaymentPlanNode,
        filterset_class=PaymentPlanFilter,
        permission_classes=(hopePermissionClass(Permissions.PAYMENT_MODULE_VIEW_LIST),),
    )
    payment_plan_status_choices = graphene.List(ChoiceObject)
    currency_choices = graphene.List(ChoiceObject)
    all_delivery_mechanisms = graphene.List(ChoiceObject)
    payment_plan_background_action_status_choices = graphene.List(ChoiceObject)
    available_fsps_for_delivery_mechanisms = graphene.List(
        FspChoices,
        input=AvailableFspsForDeliveryMechanismsInput(),
    )
    all_cash_plans_and_payment_plans = graphene.Field(
        PaginatedCashPlanAndPaymentPlanNode,
        business_area=graphene.String(required=True),
        program=graphene.String(),
        search=graphene.String(),
        service_provider=graphene.String(),
        delivery_type=graphene.List(graphene.String),
        verification_status=graphene.List(graphene.String),
        start_date_gte=graphene.String(),
        end_date_lte=graphene.String(),
        order_by=graphene.String(),
        first=graphene.Int(),
        last=graphene.Int(),
        before=graphene.String(),
        after=graphene.String(),
    )

    def resolve_available_fsps_for_delivery_mechanisms(self, info: Any, input: Dict, **kwargs: Any) -> List:
        payment_plan = get_object_or_404(PaymentPlan, id=decode_id_string(input["payment_plan_id"]))
        delivery_mechanisms = (
            DeliveryMechanismPerPaymentPlan.objects.filter(payment_plan=payment_plan)
            .values_list("delivery_mechanism", flat=True)
            .order_by("delivery_mechanism_order")
        )

        def get_fsps_for_delivery_mechanism(mechanism: str) -> List:
            fsps = FinancialServiceProvider.objects.filter(delivery_mechanisms__contains=[mechanism]).distinct()
            return (
                [
                    # This basically checks if FSP can accept ANY additional volume,
                    # more strict validation is performed in AssignFspToDeliveryMechanismMutation
                    {"id": fsp.id, "name": fsp.name}
                    for fsp in fsps
                    if fsp.can_accept_any_volume()
                ]
                if fsps
                else []
            )

        return [
            {"delivery_mechanism": mechanism, "fsps": get_fsps_for_delivery_mechanism(mechanism)}
            for mechanism in delivery_mechanisms
        ]

    def resolve_all_payment_verifications(self, info: Any, **kwargs: Any) -> QuerySet:
        payment_qs = Payment.objects.filter(id=OuterRef("payment_object_id"), household__withdrawn=True)
        payment_record_qs = Payment.objects.filter(id=OuterRef("payment_object_id"), household__withdrawn=True)

        return (
            PaymentVerification.objects.filter(
                Q(payment_verification_plan__status=PaymentVerificationPlan.STATUS_ACTIVE)
                | Q(payment_verification_plan__status=PaymentVerificationPlan.STATUS_FINISHED)
            )
            .annotate(
                payment_obj__household__status=Case(
                    When(Exists(payment_qs), then=Value(STATUS_INACTIVE)),
                    When(Exists(payment_record_qs), then=Value(STATUS_INACTIVE)),
                    default=Value(STATUS_ACTIVE),
                    output_field=CharField(),
                ),
            )
            .distinct()
        )

    def resolve_sample_size(self, info: Any, input: Dict, **kwargs: Any) -> Dict[str, int]:
        node_name, obj_id = b64decode(input["cash_or_payment_plan_id"]).decode().split(":")
        payment_plan_object: Union["PaymentPlan", "CashPlan"] = get_object_or_404(  # type: ignore
            CashPlan if node_name == "CashPlanNode" else PaymentPlan, id=obj_id
        )

        def get_payment_records(
            obj: Union["PaymentPlan", "CashPlan"],
            payment_verification_plan: Optional[PaymentVerificationPlan],
            verification_channel: str,
        ) -> QuerySet:
            kw: Dict = {}
            if payment_verification_plan:
                kw["payment_verification_plan"] = payment_verification_plan
            if verification_channel == PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO:
                kw["extra_validation"] = does_payment_record_have_right_hoh_phone_number
            kw["class_name"] = obj.__class__.__name__
            return obj.available_payment_records(**kw)

        payment_verification_plan = None
        if payment_verification_plan_id := decode_id_string(input.get("payment_verification_plan_id")):
            payment_verification_plan = get_object_or_404(PaymentVerificationPlan, id=payment_verification_plan_id)

        payment_records = get_payment_records(
            payment_plan_object, payment_verification_plan, input["verification_channel"]
        )
        if not payment_records:
            return {
                "sample_size": 0,
                "payment_record_count": 0,
            }

        sampling = Sampling(input, payment_plan_object, payment_records)
        payment_record_count, payment_records_sample_count = sampling.generate_sampling()

        return {
            "payment_record_count": payment_record_count,
            "sample_size": payment_records_sample_count,
        }

    def resolve_all_rapid_pro_flows(self, info: Any, business_area_slug: str, **kwargs: Any) -> List[RapidProFlow]:
        api = RapidProAPI(business_area_slug)
        return api.get_flows()

    def resolve_payment_record_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentRecord.STATUS_CHOICE)

    def resolve_payment_record_entitlement_card_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE)

    def resolve_payment_record_delivery_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentRecord.DELIVERY_TYPE_CHOICE)

    def resolve_cash_plan_verification_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.STATUS_CHOICES)

    def resolve_cash_plan_verification_sampling_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.SAMPLING_CHOICES)

    def resolve_cash_plan_verification_verification_channel_choices(
        self, info: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerificationPlan.VERIFICATION_CHANNEL_CHOICES)

    def resolve_payment_verification_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentVerification.STATUS_CHOICES)

    def resolve_all_delivery_mechanisms(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GenericPayment.DELIVERY_TYPE_CHOICE)

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment_verification(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        filters = chart_filters_decoder(kwargs)
        status_choices_mapping = chart_map_choices(PaymentVerification.STATUS_CHOICES)
        additional_filters: Q = chart_create_filter_query_for_payment_verification_gfk(
            filters,
            program_id_path="payment__parent__program__id,payment_record__parent__program__id",
            administrative_area_path="payment__household__admin_area,payment_record__parent__program__id",
        )
        payment_verifications = chart_get_filtered_qs(
            PaymentVerification.objects,
            year,
            business_area_slug_filter={
                "payment__business_area__slug": business_area_slug,
                "payment_record__business_area__slug": business_area_slug,
            },
            additional_filters=additional_filters,
            year_filter_path="payment__delivery_date,payment_record__delivery_date",
            payment_verification_gfk=True,
        )

        verifications_by_status = payment_verifications.values("status").annotate(count=Count("status"))
        verifications_by_status_dict = {x.get("status"): x.get("count") for x in verifications_by_status}
        dataset: List[int] = [verifications_by_status_dict.get(status, 0) for status in status_choices_mapping.keys()]
        try:
            all_verifications = sum(dataset)
            dataset_percentage = [data / all_verifications for data in dataset]
        except ZeroDivisionError:
            dataset_percentage = [0] * len(status_choices_mapping.values())
        dataset_percentage_done = [
            {"label": status, "data": [dataset_percentage_value]}
            for (dataset_percentage_value, status) in zip(dataset_percentage, status_choices_mapping.values())
        ]

        samples_count = payment_verifications.distinct("payment").count()
        all_payment_records_for_created_verifications = (
            PaymentRecord.objects.filter(
                parent__in=payment_verifications.distinct("payment_verification_plan__payment_plan").values_list(
                    "payment_verification_plan__payment_plan", flat=True
                )
            )
            .filter(status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0)
            .count()
        )
        average_sample_size: float = (
            0.0
            if all_payment_records_for_created_verifications == 0
            else samples_count / all_payment_records_for_created_verifications
        )
        return {
            "labels": ["Payment Verification"],
            "datasets": dataset_percentage_done,
            "households": payment_verifications.distinct("payment__household").count(),
            "average_sample_size": average_sample_size,
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_volume_by_delivery_mechanism(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        volume_by_delivery_type = (
            payment_items_qs.values("delivery_type")
            .order_by("delivery_type")
            .annotate(volume=Sum("delivered_quantity_usd"))
            .merge_by(
                "delivery_type",
                aggregated_fields=["volume"],
            )
        )

        labels = []
        data = []
        for volume_dict in volume_by_delivery_type:
            if volume_dict.get("volume"):
                labels.append(volume_dict.get("delivery_type"))
                data.append(volume_dict.get("volume"))

        return {"labels": labels, "datasets": [{"data": data}]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_payment(self, info: Any, business_area_slug: str, year: int, **kwargs: Any) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        )
        payment_items_dict = payment_items_qs.aggregate(
            successful=Count("id", filter=~Q(status=GenericPayment.STATUS_ERROR)),
            unsuccessful=Count("id", filter=Q(status=GenericPayment.STATUS_ERROR)),
        )

        dataset = [
            {
                "data": [
                    payment_items_dict.get("successful", 0),
                    payment_items_dict.get("unsuccessful", 0),
                ]
            }
        ]

        return {"labels": ["Successful Payments", "Unsuccessful Payments"], "datasets": dataset}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_total_transferred(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs)
        )
        return {"total": payment_items_qs.aggregate(Sum("delivered_quantity_usd"))["delivered_quantity_usd__sum"]}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_table_total_cash_transferred_by_administrative_area(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        if business_area_slug == "global":
            return None
        order = kwargs.pop("order", None)
        order_by = kwargs.pop("order_by", None)
        payment_items_ids = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).values_list("id", flat=True)

        admin_areas = (
            Area.objects.filter(
                Q(household__paymentrecord__id__in=payment_items_ids) | Q(household__payment__id__in=payment_items_ids),
                area_type__area_level=2,
            )
            .distinct()
            .annotate(
                total_transferred_payment_records=Sum("household__paymentrecord__delivered_quantity_usd"),
                total_transferred_payments=Sum("household__payment__delivered_quantity_usd"),
            )
            .annotate(
                num_households=Count("household", distinct=True),
                total_transferred=F("total_transferred_payments") + F("total_transferred_payment_records"),
            )
        )

        if order_by:
            order_by_arg = None
            if order_by == "admin2":
                order_by_arg = "name"
            elif order_by == "totalCashTransferred":
                order_by_arg = "total_transferred"
            elif order_by == "totalHouseholds":
                order_by_arg = "num_households"
            if order_by_arg:
                admin_areas = admin_areas.order_by(f"{'-' if order == 'desc' else ''}{order_by_arg}")

        data = [
            {
                "id": item.id,
                "admin2": item.name,
                "total_cash_transferred": item.total_transferred,
                "total_households": item.num_households,
            }
            for item in admin_areas
        ]

        return {"data": data}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_total_transferred_cash_by_country(self, info: Any, year: int, **kwargs: Any) -> Dict[str, Any]:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(year, "global", {}, True)

        countries_and_amounts: dict = (
            payment_items_qs.select_related("business_area")
            .values("business_area")
            .order_by("business_area")
            .annotate(
                total_delivered_cash=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_CASH)
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_VOUCHER)
                ),
                business_area_name=F("business_area__name"),
            )
            .order_by("business_area_name")
            .merge_by("business_area_name", aggregated_fields=["total_delivered_cash", "total_delivered_voucher"])
        )

        labels = []
        cash_transferred = []
        voucher_transferred = []
        total_transferred = []
        for data_dict in countries_and_amounts:
            labels.append(data_dict.get("business_area_name"))
            cash_transferred.append(data_dict.get("total_delivered_cash") or 0)
            voucher_transferred.append(data_dict.get("total_delivered_voucher") or 0)
            total_transferred.append(cash_transferred[-1] + voucher_transferred[-1])

        datasets = [
            {"label": "Actual cash transferred", "data": cash_transferred},
            {"label": "Actual voucher transferred", "data": voucher_transferred},
            {"label": "Total transferred", "data": total_transferred},
        ]

        return {"labels": labels, "datasets": datasets}

    def resolve_currency_choices(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object([c for c in CURRENCY_CHOICES if c[0] != ""])

    def resolve_payment_plan_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlan.Status.choices)

    def resolve_payment_plan_background_action_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PaymentPlan.BackgroundActionStatus.choices)

    def resolve_all_cash_plans_and_payment_plans(self, info: Any, **kwargs: Any) -> Dict[str, Any]:
        service_provider_qs = ServiceProvider.objects.filter(cash_plans=OuterRef("pk")).distinct()
        fsp_qs = FinancialServiceProvider.objects.filter(
            delivery_mechanisms_per_payment_plan__payment_plan=OuterRef("pk")
        ).distinct()
        delivery_mechanisms_per_pp_qs = DeliveryMechanismPerPaymentPlan.objects.filter(
            payment_plan=OuterRef("pk")
        ).distinct("delivery_mechanism")
        payment_verification_summary_qs = PaymentVerificationSummary.objects.filter(
            payment_plan_object_id=OuterRef("id")
        )

        payment_plan_qs = PaymentPlan.objects.filter(status=PaymentPlan.Status.FINISHED).annotate(
            fsp_names=ArraySubquery(fsp_qs.values_list("name", flat=True)),
            delivery_types=ArraySubquery(delivery_mechanisms_per_pp_qs.values_list("delivery_mechanism", flat=True)),
        )
        cash_plan_qs = CashPlan.objects.all().annotate(
            unicef_id=F("ca_id"),
            fsp_names=ArraySubquery(service_provider_qs.values_list("full_name", flat=True)),
            delivery_types=Func(
                [],
                F("delivery_type"),
                function="array_append",
                output_field=ArrayField(CharField(null=True)),
            ),
        )
        qs = (
            ExtendedQuerySetSequence(payment_plan_qs, cash_plan_qs)
            .annotate(
                custom_order=Case(
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_ACTIVE)),
                        then=Value(1),
                    ),
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_PENDING)),
                        then=Value(2),
                    ),
                    When(
                        Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_FINISHED)),
                        then=Value(3),
                    ),
                    output_field=IntegerField(),
                    default=Value(0),
                ),
            )
            .order_by("-updated_at", "custom_order")
        )

        # filtering
        qs: Iterable = cash_plan_and_payment_plan_filter(qs, **kwargs)  # type: ignore

        # ordering
        if order_by_value := kwargs.get("order_by"):
            qs = cash_plan_and_payment_plan_ordering(qs, order_by_value)

        # add qraphql pagination
        resp = connection_from_list_slice(
            qs,
            args=kwargs,
            connection_type=PaginatedCashPlanAndPaymentPlanNode,
            edge_type=CashPlanAndPaymentPlanEdges,
            pageinfo_type=PageInfoNode,
            list_length=len(qs),
        )
        resp.total_count = len(qs)

        return resp
