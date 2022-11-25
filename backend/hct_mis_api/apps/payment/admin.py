from typing import Any, Optional
from uuid import UUID

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, HttpRequest
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.depot.widget import DepotManager
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from adminfilters.querystring import QueryStringFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.payment.models import (
    CashPlanPaymentVerification,
    PaymentRecord,
    PaymentVerification,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(PaymentRecord)
class PaymentRecordAdmin(AdminAdvancedFiltersMixin, LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("household", "status", "cash_plan_name", "target_population")
    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("target_population", AutoCompleteFilter),
        ("cash_plan", AutoCompleteFilter),
        ("service_provider", AutoCompleteFilter),
        # ValueFilter.factory("cash_plan__id", "CashPlan ID"),
        # ValueFilter.factory("target_population__id", "TargetPopulation ID"),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("service_provider__name", "Service Provider"),
        ("cash_plan__name", "CashPlan"),
        ("target_population__name", "TargetPopulation"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "cash_plan",
        "household",
        "head_of_household",
        "target_population",
        "service_provider",
    )

    def cash_plan_name(self, obj: Any) -> str:
        return obj.cash_plan.name

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related("household", "cash_plan", "service_provider", "target_population", "business_area")
        )


@admin.register(CashPlanPaymentVerification)
class CashPlanPaymentVerificationAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = ("cash_plan", "status", "verification_channel")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
        ("cash_plan", AutoCompleteFilter),
        ("cash_plan__business_area", AutoCompleteFilter),
    )
    date_hierarchy = "updated_at"
    search_fields = ("cash_plan__name",)
    raw_id_fields = ("cash_plan",)

    @button()
    def verifications(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?cash_plan_payment_verification__exact={pk}"
        return HttpResponseRedirect(url)

    @button()
    def execute_sync_rapid_pro(self, request: HttpRequest) -> Optional[HttpResponseRedirect]:
        if request.method == "POST":
            from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
                CheckRapidProVerificationTask,
            )

            task = CheckRapidProVerificationTask()
            task.execute()
            self.message_user(request, "Rapid Pro synced", messages.SUCCESS)
        else:
            return confirm_action(
                self,
                request,
                self.execute_sync_rapid_pro,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                        <h3>Import will only be simulated</h3>
                        """
                ),
                "Successfully executed",
                template="admin_extra_buttons/confirm.html",
            )

    def activate(self, request: HttpRequest, pk: UUID) -> TemplateResponse:
        return confirm_action(
            self,
            request,
            lambda _: VerificationPlanStatusChangeServices(CashPlanPaymentVerification.objects.get(pk=pk)).activate(),
            "This action will trigger Cash Plan Payment Verification activation (also sending messages via Rapid Pro).",
            "Successfully activated.",
        )


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(HOPEModelAdminBase):
    list_display = ("household", "status", "received_amount", "cash_plan_name")

    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        ("cash_plan_payment_verification__cash_plan", AutoCompleteFilter),
        ("cash_plan_payment_verification__cash_plan__business_area", AutoCompleteFilter),
        ("payment_record__household__unicef_id", ValueFilter),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("payment_record", "cash_plan_payment_verification")

    def cash_plan_name(self, obj: Any) -> str:
        return obj.cash_plan_payment_verification.cash_plan.name

    def household(self, obj: Any) -> str:
        return obj.payment_record.household.unicef_id

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "cash_plan_payment_verification",
                "cash_plan_payment_verification__cash_plan",
                "payment_record",
                "payment_record__household",
            )
        )


@admin.register(ServiceProvider)
class ServiceProviderAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "short_name", "country")
    search_fields = ("full_name", "vision_id", "short_name")
    list_filter = (("business_area", AutoCompleteFilter),)
    autocomplete_fields = ("business_area",)
