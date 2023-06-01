from base64 import b64decode
from typing import Any, List
from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, CharField, Count, Q, QuerySet, Value, When
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from django_filters import (
    BooleanFilter,
    CharFilter,
    ChoiceFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
    OrderingFilter,
    UUIDFilter,
)

from hct_mis_api.apps.activity_log.schema import LogEntryFilter
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.utils import (
    CustomOrderingFilter,
    decode_id_string,
    is_valid_uuid,
)
from hct_mis_api.apps.household.models import ROLE_NO_ROLE
from hct_mis_api.apps.payment.models import (
    CashPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    FinancialServiceProviderXlsxTemplate,
    GenericPayment,
    Payment,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)
from hct_mis_api.apps.program.models import Program


class PaymentRecordFilter(FilterSet):
    individual = CharFilter(method="individual_filter")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = (
            "parent",
            "household",
        )
        model = PaymentRecord

    order_by = CustomOrderingFilter(
        fields=(
            "ca_id",
            "status",
            Lower("name"),
            "status_date",
            Lower("head_of_household__full_name"),
            "total_person_covered",
            "distribution_modality",
            "household__unicef_id",
            "household__size",
            "entitlement_quantity",
            "delivered_quantity_usd",
            "delivery_date",
        )
    )

    def individual_filter(self, qs: QuerySet, name: str, value: UUID) -> QuerySet:
        if is_valid_uuid(str(value)):
            return qs.exclude(household__individuals_and_roles__role=ROLE_NO_ROLE)
        return qs


class PaymentVerificationFilter(FilterSet):
    payment_plan_id = CharFilter(method="payment_plan_filter")
    search = CharFilter(method="search_filter")
    business_area = CharFilter(method="business_area_filter", required=True)
    verification_channel = CharFilter(field_name="payment_verification_plan__verification_channel")

    class Meta:
        fields = ("payment_verification_plan", "status")
        model = PaymentVerification

    order_by = OrderingFilter(
        fields=(
            "payment__unicef_id",
            "payment_record__ca_id",
            "payment_verification_plan__verification_channel",
            "payment_verification_plan__unicef_id",
            "status",
            "received_amount",
            "payment__head_of_household__family_name",
            "payment__household__unicef_id",
            "payment__household__status",
            "payment__delivered_quantity",
            "payment__head_of_household__phone_no",
            "payment__head_of_household__phone_no_alternative",
        )
    )

    def search_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(payment__unicef_id__istartswith=value)
            q_obj |= Q(payment_record__ca_id__istartswith=value)
            q_obj |= Q(payment_verification_plan__unicef_id__istartswith=value)
            q_obj |= Q(received_amount__istartswith=value)
            q_obj |= Q(payment__household__unicef_id__istartswith=value)
            q_obj |= Q(payment__head_of_household__full_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__given_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__middle_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__family_name__istartswith=value)
            q_obj |= Q(payment__head_of_household__phone_no__istartswith=value)
            q_obj |= Q(payment__head_of_household__phone_no_alternative__istartswith=value)
            q_obj |= Q(payment_record__household__unicef_id__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__full_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__given_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__middle_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__family_name__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__phone_no__istartswith=value)
            q_obj |= Q(payment_record__head_of_household__phone_no_alternative__istartswith=value)

        return qs.filter(q_obj)

    def payment_plan_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        node_name, obj_id = b64decode(value).decode().split(":")
        # content type for PaymentPlan or CashPlan
        ct_id = ContentType.objects.filter(app_label="payment", model=node_name[:-4].lower()).first().pk
        return qs.filter(
            payment_verification_plan__payment_plan_object_id=obj_id,
            payment_verification_plan__payment_plan_content_type_id=ct_id,
        )

    def business_area_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(
            Q(payment_verification_plan__payment_plan__business_area__slug=value)
            | Q(payment_verification_plan__cash_plan__business_area__slug=value)
        )


class PaymentVerificationPlanFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = PaymentVerificationPlan


class PaymentVerificationSummaryFilter(FilterSet):
    class Meta:
        fields = tuple()
        model = PaymentVerificationSummary


class PaymentVerificationLogEntryFilter(LogEntryFilter):
    PLAN_TYPE_CASH = "CashPlan"
    PLAN_TYPE_PAYMENT = "PaymentPlan"
    PLAN_TYPE_CHOICES = (
        (PLAN_TYPE_CASH, _("CashPlan")),
        (PLAN_TYPE_PAYMENT, _("PaymentPlan")),
    )
    object_id = UUIDFilter(method="object_id_filter")
    object_type = ChoiceFilter(method="object_type_filter", choices=PLAN_TYPE_CHOICES)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        cleaned_data = self.form.cleaned_data
        object_type = cleaned_data.get("object_type")
        object_id = cleaned_data.get("object_id")
        plan_object = (PaymentPlan if object_type == self.PLAN_TYPE_PAYMENT else CashPlan).objects.get(pk=object_id)
        verifications_ids = plan_object.payment_verification_plan.all().values_list("pk", flat=True)
        return queryset.filter(object_id__in=verifications_ids)

    def object_id_filter(self, qs: QuerySet, name: str, value: UUID) -> QuerySet:
        cash_plan = CashPlan.objects.get(pk=value)
        verifications_ids = cash_plan.verifications.all().values_list("pk", flat=True)
        return qs.filter(object_id__in=verifications_ids)


class FinancialServiceProviderXlsxTemplateFilter(FilterSet):
    class Meta:
        fields = (
            "name",
            "created_by",
        )
        model = FinancialServiceProviderXlsxTemplate

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "created_by",
        )
    )


class FinancialServiceProviderXlsxReportFilter(FilterSet):
    class Meta:
        fields = ("status",)
        model = FinancialServiceProviderXlsxReport

    order_by = CustomOrderingFilter(fields=("status",))


class FinancialServiceProviderFilter(FilterSet):
    delivery_mechanisms = MultipleChoiceFilter(
        field_name="delivery_mechanisms", choices=GenericPayment.DELIVERY_TYPE_CHOICE
    )

    class Meta:
        fields = (
            "created_by",
            "name",
            "vision_vendor_number",
            "delivery_mechanisms",
            "distribution_limit",
            "communication_channel",
            "xlsx_templates",
        )
        model = FinancialServiceProvider

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("name"),
            "vision_vendor_number",
            "delivery_mechanisms",
            "distribution_limit",
            "communication_channel",
        )
    )


class CashPlanFilter(FilterSet):
    search = CharFilter(method="search_filter")
    delivery_type = MultipleChoiceFilter(field_name="delivery_type", choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    verification_status = MultipleChoiceFilter(
        field_name="payment_verification_summary__status", choices=PaymentVerificationPlan.STATUS_CHOICES
    )
    business_area = CharFilter(
        field_name="business_area__slug",
    )

    class Meta:
        fields = {
            "program": ["exact"],
            "assistance_through": ["exact", "startswith"],
            "service_provider__full_name": ["exact", "startswith"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
            "business_area": ["exact"],
        }
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "ca_id",
            "status",
            "total_number_of_hh",
            "total_entitled_quantity",
            ("payment_verification_summary__status", "verification_status"),
            "total_persons_covered",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_date",
            "assistance_measurement",
            "assistance_through",
            "delivery_type",
            "start_date",
            "end_date",
            "program__name",
            "id",
            "updated_at",
            "service_provider__full_name",
        )
    )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = queryset.annotate(total_number_of_hh=Count("payment_items"))
        return super().filter_queryset(queryset)

    def search_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(ca_id__istartswith=value)
        return qs.filter(q_obj)


class PaymentPlanFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=PaymentPlan.Status.choices)
    total_entitled_quantity_from = NumberFilter(field_name="total_entitled_quantity", lookup_expr="gte")
    total_entitled_quantity_to = NumberFilter(field_name="total_entitled_quantity", lookup_expr="lte")
    dispersion_start_date = DateFilter(field_name="dispersion_start_date", lookup_expr="gte")
    dispersion_end_date = DateFilter(field_name="dispersion_end_date", lookup_expr="lte")
    is_follow_up = BooleanFilter(field_name="is_follow_up")
    source_payment_plan_id = CharFilter(method="source_payment_plan_filter")

    class Meta:
        fields = tuple()
        model = PaymentPlan

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        queryset = queryset.annotate(total_number_of_hh=Count("payment_items"))
        if not self.form.cleaned_data.get("order_by"):
            queryset = queryset.order_by("unicef_id")
        return super().filter_queryset(queryset)

    order_by = OrderingFilter(
        fields=(
            "unicef_id",
            "status",
            "total_households_count",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_start_date",
            "dispersion_end_date",
            "created_at",
        )
    )

    def search_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(Q(id__icontains=value) | Q(unicef_id__icontains=value))

    def source_payment_plan_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return PaymentPlan.objects.filter(source_payment_plan_id=decode_id_string(value))


class PaymentFilter(FilterSet):
    business_area = CharFilter(field_name="parent__business_area__slug", required=True)
    payment_plan_id = CharFilter(required=True, method="payment_plan_id_filter")

    def payment_plan_id_filter(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        payment_plan_id = decode_id_string(value)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)
        q = Q(parent=payment_plan)
        if payment_plan.status != PaymentPlan.Status.OPEN:
            qs = qs.eligible()
        else:
            qs = qs.exclude(excluded=True)

        return qs.filter(q)

    class Meta:
        fields = tuple()
        model = Payment

    order_by = OrderingFilter(
        fields=(
            "unicef_id",
            "status",
            "household_id",
            "household__size",
            "admin2",
            "collector_id",
            "entitlement_quantity_usd",
            "delivered_quantity",
            "financial_service_provider__name",
            "parent__program__name",
            "delivery_date",
        )
    )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        # household__admin2
        queryset = queryset.annotate(
            admin2=Case(
                When(
                    household__admin_area__isnull=True,
                    then=Value(""),
                ),
                When(
                    household__admin_area__isnull=False,
                    household__admin_area__area_type__area_level__in=(0, 1),
                    then=Value(""),
                ),
                When(
                    household__admin_area__isnull=False,
                    household__admin_area__area_type__area_level__lt=2,
                    household__admin_area__area_type__area_level__gt=2,
                    then=Lower("household__admin_area__parent__name"),
                ),
                When(
                    household__admin_area__isnull=False,
                    then=Lower("household__admin_area__name"),
                ),
                default=Value(""),
                output_field=CharField(),
            )
        ).select_related("financial_service_provider")
        if not self.form.cleaned_data.get("order_by"):
            queryset = queryset.order_by("unicef_id")

        return super().filter_queryset(queryset)


def cash_plan_and_payment_plan_filter(queryset: ExtendedQuerySetSequence, **kwargs: Any) -> ExtendedQuerySetSequence:
    business_area = kwargs.get("business_area")
    program = kwargs.get("program")
    service_provider = kwargs.get("service_provider")
    delivery_types = kwargs.get("delivery_type")
    verification_status = kwargs.get("verification_status")
    start_date_gte, end_date_lte = kwargs.get("start_date_gte"), kwargs.get("end_date_lte")
    search = kwargs.get("search")

    if business_area:
        queryset = queryset.filter(business_area__slug=business_area)

    if program:
        program_obj = get_object_or_404(Program, id=decode_id_string(program))
        queryset = queryset.filter(program=program_obj)

    if start_date_gte:
        queryset = queryset.filter(start_date__gte=start_date_gte)
    if end_date_lte:
        queryset = queryset.filter(end_date__lte=end_date_lte)

    if verification_status:
        queryset = queryset.filter(payment_verification_summary__status__in=verification_status)

    if service_provider:
        queryset = queryset.filter(fsp_names__icontains=service_provider)

    if delivery_types:
        q = Q()
        for delivery_type in delivery_types:
            q |= Q(delivery_types__icontains=delivery_type)
        queryset = queryset.filter(q)

    if search:
        q = Q()
        values = search.split(" ")
        for value in values:
            q |= Q(unicef_id__istartswith=value)
        queryset = queryset.filter(q)

    return queryset


def cash_plan_and_payment_plan_ordering(queryset: ExtendedQuerySetSequence, order_by: str) -> List[Any]:
    reverse = "-" if order_by.startswith("-") else ""
    order_by = order_by[1:] if reverse else order_by

    if order_by == "verification_status":
        qs = queryset.order_by(reverse + "custom_order")
    elif order_by == "unicef_id":
        qs = sorted(queryset, key=lambda o: o.get_unicef_id, reverse=bool(reverse))
    else:
        qs = queryset.order_by(reverse + order_by)

    return list(qs)


def payment_record_and_payment_filter(queryset: ExtendedQuerySetSequence, **kwargs: Any) -> ExtendedQuerySetSequence:
    business_area = kwargs.get("business_area")
    household = kwargs.get("household")

    if business_area:
        queryset = queryset.filter(business_area__slug=business_area)

    if household:
        queryset = queryset.filter(household__id=decode_id_string(household))

    return queryset


def payment_record_and_payment_ordering(queryset: ExtendedQuerySetSequence, order_by: str) -> List[Any]:
    reverse = "-" if order_by.startswith("-") else ""
    order_by = order_by[1:] if reverse else order_by

    if order_by == "ca_id":
        qs = sorted(queryset, key=lambda o: o.get_unicef_id, reverse=bool(reverse))
    elif order_by in ("head_of_household", "entitlement_quantity", "delivered_quantity", "delivery_date"):
        order_by_dict = {f"{order_by}__isnull": True}
        qs_null = list(queryset.filter(**order_by_dict))
        if reverse:
            qs = list(queryset.exclude(**order_by_dict).order_by(f"-{order_by}")) + qs_null
        else:
            qs = qs_null + list(queryset.exclude(**order_by_dict).order_by(order_by))
    else:
        qs = queryset.order_by(reverse + order_by)

    return list(qs)
