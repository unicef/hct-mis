from typing import Iterable

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    Case,
    CharField,
    Count,
    Exists,
    F,
    Func,
    IntegerField,
    OuterRef,
    QuerySet,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from django_filters import rest_framework as filters
from requests import Request
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from hct_mis_api.apps.account.api.permissions import (
    hopeRestPermissionClass,
    hopeRestPermissionNoGPFClass,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.core.utils import decode_id_string, get_program_id_from_headers
from hct_mis_api.apps.payment.api.serializers import (
    PaymentPlanBulkActionSerializer,
    PaymentPlanSerializer,
    PaymentVerificationSerializer,
)
from hct_mis_api.apps.payment.filters import (
    PaymentPlanFilter,
    cash_plan_and_payment_plan_filter,
    cash_plan_and_payment_plan_ordering,
)
from hct_mis_api.apps.payment.managers import ArraySubquery
from hct_mis_api.apps.payment.models import (
    CashPlan,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService


class PaymentPlanViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentPlanSerializer
    permission_classes = [
        IsAuthenticated,
        hopeRestPermissionClass(Permissions.PM_VIEW_LIST),
        hopeRestPermissionNoGPFClass(Permissions.PAYMENT_VIEW_LIST_NO_GPF),
    ]
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = PaymentPlanFilter
    search_fields = (
        "unicef_id",
        "id",
        "^name",
    )

    def get_queryset(self) -> QuerySet:
        business_area = get_object_or_404(BusinessArea, slug=self.request.headers.get("Business-Area"))
        queryset = PaymentPlan.objects.filter(business_area=business_area)
        if get_program_id_from_headers(self.request.headers):
            return queryset
        program_ids = self.request.user.partner.get_program_ids_for_business_area(str(business_area.id))
        return queryset.filter(
            status__in=[
                PaymentPlan.Status.IN_APPROVAL,
                PaymentPlan.Status.IN_AUTHORIZATION,
                PaymentPlan.Status.IN_REVIEW,
            ],
            program__in=program_ids,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="status-action-mapping",
        permission_classes=[],
    )
    def status_action_mapping(self, request, *args, **kwargs):
        return Response(
            {
                PaymentPlan.Status.IN_APPROVAL.name: "Approve",
                PaymentPlan.Status.IN_AUTHORIZATION.name: "Authorize",
                PaymentPlan.Status.IN_REVIEW.name: "Release",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="has-none-program-permission",
        permission_classes=[],
    )
    def has_none_program_permission(self, request, *args, **kwargs):
        return Response(
            {
                "has-none-program-permission": request.user.has_permission(
                    Permissions.PAYMENT_VIEW_LIST_NO_GPF,
                    business_area=get_object_or_404(BusinessArea, slug=self.request.headers.get("Business-Area")),
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-action",
        serializer_class=PaymentPlanBulkActionSerializer,
    )
    def bulk_action(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action_name = serializer.validated_data["action"]
            comment = serializer.validated_data.get("comment", "")
            input_data = {"action": action_name, "comment": comment}
            business_area = get_object_or_404(BusinessArea, slug=self.request.headers.get("Business-Area"))

            for payment_plan_id_str in serializer.validated_data["ids"]:
                self._perform_payment_plan_status_action(
                    payment_plan_id_str,
                    input_data,
                    business_area,
                    request,
                )

        return Response(status=status.HTTP_200_OK)

    def _perform_payment_plan_status_action(
        self,
        payment_plan_id_str: str,
        input_data: dict,
        business_area: BusinessArea,
        request: Request,
    ):
        payment_plan_id = decode_id_string(payment_plan_id_str)
        payment_plan = get_object_or_404(PaymentPlan, id=payment_plan_id)

        old_payment_plan = copy_model_object(payment_plan)
        if old_payment_plan.imported_file:
            old_payment_plan.imported_file = copy_model_object(payment_plan.imported_file)
        if old_payment_plan.export_file_entitlement:
            old_payment_plan.export_file_entitlement = copy_model_object(payment_plan.export_file_entitlement)
        if old_payment_plan.export_file_per_fsp:
            old_payment_plan.export_file_per_fsp = copy_model_object(payment_plan.export_file_per_fsp)

        if not self.request.user.has_permission(
            self._get_action_permission(input_data["action"]),
            business_area,
            payment_plan.program_id,
        ):
            raise PermissionDenied(
                f"You do not have permission to perform action {input_data['action']} "
                f"on payment plan with id {payment_plan.unicef_id}."
            )

        payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
            input_data=input_data, user=request.user
        )
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=request.user,
            programs=payment_plan.get_program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

    def _get_action_permission(self, action_name: str) -> Permissions:
        action_to_permissions_map = {
            PaymentPlan.Action.APPROVE.name: Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name,
            PaymentPlan.Action.AUTHORIZE.name: Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name,
            PaymentPlan.Action.REVIEW.name: Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name,
        }
        return action_to_permissions_map.get(action_name)


class PaymentVerificationListView(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [
        hopeRestPermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopeRestPermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),
        hopeRestPermissionNoGPFClass(Permissions.PAYMENT_VIEW_LIST_NO_GPF),
    ]
    serializer_class = PaymentVerificationSerializer
    queryset = PaymentVerification.objects.none()

    def list(self, request, *args, **kwargs) -> Response:
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

        if "is_payment_verification_page" in self.request.query_params and self.request.query_params.get(
            "is_payment_verification_page"
        ):
            payment_plan_qs = PaymentPlan.objects.filter(status=PaymentPlan.Status.FINISHED)
        else:
            payment_plan_qs = PaymentPlan.objects.all()

        payment_plan_qs = payment_plan_qs.annotate(
            fsp_names=ArraySubquery(fsp_qs.values_list("name", flat=True)),
            delivery_types=ArraySubquery(delivery_mechanisms_per_pp_qs.values_list("delivery_mechanism", flat=True)),
            currency_order=F("currency"),
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
            currency_order=PaymentRecord.objects.filter(parent_id=OuterRef("id")).values("currency")[:1],
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
                total_number_of_households=Count("payment_items"),
                total_entitled_quantity_order=Coalesce(
                    "total_entitled_quantity", 0, output_field=models.DecimalField()
                ),
                total_delivered_quantity_order=Coalesce(
                    "total_delivered_quantity", 0, output_field=models.DecimalField()
                ),
                total_undelivered_quantity_order=Coalesce(
                    "total_undelivered_quantity", 0, output_field=models.DecimalField()
                ),
            )
            .order_by("-updated_at", "custom_order")
        )

        # filtering
        search_kwargs = {
            key: val[0] if isinstance(val, list) else val for key, val in self.request.query_params.items()
        }
        search_kwargs["business_area"] = self.request.headers.get("Business-Area")
        queryset: Iterable = cash_plan_and_payment_plan_filter(qs, **search_kwargs)  # type: ignore

        # ordering
        if order_by_value := self.request.query_params.get("order_by"):
            queryset = cash_plan_and_payment_plan_ordering(queryset, order_by_value)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
