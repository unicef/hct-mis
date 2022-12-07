from django import forms
from typing import Any, Optional
from uuid import UUID

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
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
    CashPlan,
    DeliveryMechanism,
    DeliveryMechanismPerPaymentPlan,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxReport,
    FinancialServiceProviderXlsxTemplate,
    Payment,
    PaymentChannel,
    PaymentPlan,
    PaymentRecord,
    PaymentVerification,
    PaymentVerificationPlan,
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
        ("parent", AutoCompleteFilter),
        ("service_provider", AutoCompleteFilter),
        # ValueFilter.factory("cash_plan__id", "CashPlan ID"),
        # ValueFilter.factory("target_population__id", "TargetPopulation ID"),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("service_provider__name", "Service Provider"),
        ("parent__name", "CashPlan"),
        ("target_population__name", "TargetPopulation"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "parent",
        "household",
        "head_of_household",
        "target_population",
        "service_provider",
    )

    def cash_plan_name(self, obj: Any) -> str:
        return obj.parent.name

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("household", "parent", "target_population", "business_area")


@admin.register(PaymentVerificationPlan)
class PaymentVerificationPlanAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    # TODO: fix filtering
    list_display = ("payment_plan_obj", "status", "verification_channel")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
        # ("payment_plan", AutoCompleteFilter),
        # ("payment_plan__business_area", AutoCompleteFilter),
    )
    date_hierarchy = "updated_at"
    search_fields = ("payment_plan__name",)
    raw_id_fields = ("payment_plan",)

    @button()
    def verifications(self, request: HttpRequest, pk: UUID) -> HttpResponseRedirect:
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?payment_verification_plan__exact={pk}"
        return HttpResponseRedirect(url)

    @button()
    def execute_sync_rapid_pro(self, request: HttpRequest) -> Optional[HttpResponseRedirect]:  # type: ignore
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
            lambda _: VerificationPlanStatusChangeServices(PaymentVerificationPlan.objects.get(pk=pk)).activate(),
            "This action will trigger Cash Plan Payment Verification activation (also sending messages via Rapid Pro).",
            "Successfully activated.",
        )


@admin.register(PaymentVerification)
class PaymentVerificationAdmin(HOPEModelAdminBase):
    # TODO: update filter and get_qs
    list_display = ("household", "status", "received_amount", "payment_plan_name")

    list_filter = (
        DepotManager,
        QueryStringFilter,
        ("status", ChoicesFieldComboFilter),
        # ("payment_verification_plan__payment_plan_obj", AutoCompleteFilter),
        # ("payment_verification_plan__payment_plan_obj__business_area", AutoCompleteFilter),
        ("payment__household__unicef_id", ValueFilter),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = ("payment_verification_plan",)

    def payment_plan_name(self, obj: Any) -> str:
        payment_plan = obj.payment_verification_plan.payment_plan_obj
        return getattr(payment_plan, "name", "~no name~")

    def household(self, obj: Any) -> str:
        payment = obj.payment_obj
        return payment.household.unicef_id if payment else ""

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "payment_verification_plan",
                # "payment_verification_plan__payment_plan_obj",
                # "payment_obj",
                # "payment_obj__household",
            )
        )


@admin.register(ServiceProvider)
class ServiceProviderAdmin(HOPEModelAdminBase):
    list_display = ("full_name", "short_name", "country")
    search_fields = ("full_name", "vision_id", "short_name")
    list_filter = (("business_area", AutoCompleteFilter),)
    autocomplete_fields = ("business_area",)


@admin.register(CashPlan)
class CashPlanAdmin(HOPEModelAdminBase):
    list_display = ("name", "program", "delivery_type", "status", "verification_status", "ca_id")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("delivery_type", ChoicesFieldComboFilter),
        ("payment_verification_summary__status", ChoicesFieldComboFilter),
        ("program__id", ValueFilter),
        ("vision_id", ValueFilter),
    )
    raw_id_fields = ("business_area", "program", "service_provider")
    search_fields = ("name",)

    def verification_status(self, obj):
        return obj.get_payment_verification_summary.status if obj.get_payment_verification_summary else None

    @button()
    def payments(self, request, pk):
        context = self.get_common_context(request, pk, aeu_groups=[None], action="payments")

        return TemplateResponse(request, "admin/cashplan/payments.html", context)


@admin.register(PaymentPlan)
class PaymentPlanAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "program", "status", "target_population")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("program__id", ValueFilter),
        ("target_population", AutoCompleteFilter),
    )
    raw_id_fields = ("business_area", "program", "target_population")
    search_fields = ("id", "unicef_id")


@admin.register(Payment)
class PaymentAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = ("unicef_id", "household", "status", "parent")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("parent", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("financial_service_provider__name", "Service Provider"),
        ("parent", "Payment Plan"),
    )
    date_hierarchy = "updated_at"
    raw_id_fields = (
        "business_area",
        "parent",
        "household",
        "head_of_household",
        "financial_service_provider",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("household", "parent", "business_area")


@admin.register(DeliveryMechanismPerPaymentPlan)
class DeliveryMechanismPerPaymentPlanAdmin(HOPEModelAdminBase):
    list_display = ("delivery_mechanism_order", "delivery_mechanism", "payment_plan", "status")


@admin.register(PaymentChannel)
class PaymentChannelAdmin(HOPEModelAdminBase):
    list_display = ("individual", "delivery_mechanism_display_name")

    def delivery_mechanism_display_name(self, obj):
        return obj.delivery_mechanism


@admin.register(FinancialServiceProviderXlsxTemplate)
class FinancialServiceProviderXlsxTemplateAdmin(HOPEModelAdminBase):
    list_display = (
        "name",
        "total_selected_columns",
        "created_by",
    )
    list_filter = (("created_by", AutoCompleteFilter),)
    search_fields = ("name",)
    fields = (
        "name",
        "columns",
    )

    def total_selected_columns(self, obj):
        return f"{len(obj.columns)} of {len(FinancialServiceProviderXlsxTemplate.COLUMNS_CHOICES)}"

    total_selected_columns.short_description = "# of columns"

    def save_model(self, request, obj: FinancialServiceProviderXlsxTemplate, form, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


class FinancialServiceProviderAdminForm(forms.ModelForm):
    @staticmethod
    def locked_payment_plans_for_fsp(obj: FinancialServiceProvider) -> QuerySet[PaymentPlan]:
        return PaymentPlan.objects.filter(
            ~Q(
                status__in=[
                    PaymentPlan.Status.OPEN,
                    PaymentPlan.Status.RECONCILED,
                ],
            ),
            delivery_mechanisms__financial_service_provider=obj,
        ).distinct()

    def clean(self):
        if self.instance:
            payment_plans = self.locked_payment_plans_for_fsp(self.instance)
            if payment_plans.exists():
                raise ValidationError(
                    f"Cannot modify {self.instance}, it is assigned to following Payment Plans: {list(payment_plans)}"
                )

        return super().clean()


@admin.register(FinancialServiceProvider)
class FinancialServiceProviderAdmin(HOPEModelAdminBase):
    form = FinancialServiceProviderAdminForm

    list_display = (
        "name",
        "created_by",
        "vision_vendor_number",
        "distribution_limit",
        "communication_channel",
    )
    search_fields = ("name",)
    list_filter = ("delivery_mechanisms",)
    autocomplete_fields = ("created_by", "fsp_xlsx_template")
    list_select_related = ("created_by", "fsp_xlsx_template")
    fields = (
        ("name", "vision_vendor_number"),
        ("delivery_mechanisms", "distribution_limit"),
        ("communication_channel", "fsp_xlsx_template"),
        ("data_transfer_configuration",),
    )

    def save_model(self, request, obj: FinancialServiceProvider, form, change: bool) -> None:
        if not change:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


@admin.register(FinancialServiceProviderXlsxReport)
class FinancialServiceProviderXlsxReportAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "file")
    list_filter = ("status",)
    list_select_related = ("financial_service_provider",)
    # search_fields = ("id",)
    readonly_fields = ("file", "status", "financial_service_provider")

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(DeliveryMechanism)
class DeliveryMechanismAdmin(HOPEModelAdminBase):
    pass
