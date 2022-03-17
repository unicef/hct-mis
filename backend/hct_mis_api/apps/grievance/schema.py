import datetime
import logging

from django.core.files.storage import default_storage
from django.db import models
from django.db.models import Q
from django.db.models.functions import Coalesce

import graphene
from django_filters import (
    CharFilter,
    ChoiceFilter,
    FilterSet,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    OrderingFilter,
    TypedMultipleChoiceFilter,
    UUIDFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.core_fields_attributes import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    CORE_FIELDS_ATTRIBUTES,
    HOUSEHOLD_EDIT_ONLY_FIELDS,
    KOBO_ONLY_INDIVIDUAL_FIELDS,
    TYPE_IMAGE,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import DateTimeRangeFilter
from hct_mis_api.apps.core.models import AdminArea, FlexibleAttribute
from hct_mis_api.apps.core.schema import (
    ChoiceObject,
    FieldAttributeNode,
    _custom_dict_or_attr_resolver,
    sort_by_attr,
)
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_get_filtered_qs,
    chart_permission_decorator,
    choices_to_dict,
    encode_ids,
    nested_getattr,
    to_choice_object,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.payment.schema import PaymentRecordNode
from hct_mis_api.apps.registration_datahub.schema import DeduplicationResultNode
from hct_mis_api.apps.utils.schema import Arg, ChartDatasetNode, FlexFieldsScalar

logger = logging.getLogger(__name__)


class GrievanceTicketFilter(FilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": {
            "individual": ("full_name", "unicef_id", "phone_no", "phone_no_alternative"),
            "household": ("unicef_id",),
        },
        "sensitive_ticket_details": {
            "individual": ("full_name", "unicef_id", "phone_no", "phone_no_alternative"),
            "household": ("unicef_id",),
        },
        "individual_data_update_ticket_details": {
            "individual": ("full_name", "unicef_id", "phone_no", "phone_no_alternative"),
        },
        "add_individual_ticket_details": {"household": ("unicef_id",)},
        "system_flagging_ticket_details": {
            "golden_records_individual": ("full_name", "unicef_id", "phone_no", "phone_no_alternative")
        },
        "needs_adjudication_ticket_details": {
            "golden_records_individual": ("full_name", "unicef_id", "phone_no", "phone_no_alternative")
        },
    }
    TICKET_TYPES_WITH_FSP = (
        ("complaint_ticket_details", "payment_record__service_provider"),
        ("sensitive_ticket_details", "payment_record__service_provider"),
        ("payment_verification_ticket_details", "payment_verifications__payment_record__service_provider"),
    )

    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = TypedMultipleChoiceFilter(field_name="status", choices=GrievanceTicket.STATUS_CHOICES, coerce=int)
    fsp = CharFilter(method="fsp_filter")
    admin = ModelMultipleChoiceFilter(
        field_name="admin", method="admin_filter", queryset=AdminArea.objects.filter(admin_area_level__admin_level=2)
    )
    cash_plan = CharFilter(
        field_name="payment_verification_ticket_details",
        lookup_expr="payment_verifications__cash_plan_payment_verification__cash_plan",
    )
    created_at_range = DateTimeRangeFilter(field_name="created_at")
    permissions = MultipleChoiceFilter(choices=Permissions.choices(), method="permissions_filter")

    class Meta:
        fields = {
            "id": ["exact", "startswith"],
            "category": ["exact"],
            "area": ["exact", "startswith"],
            "assigned_to": ["exact"],
            "registration_data_import": ["exact"],
        }
        model = GrievanceTicket

    order_by = OrderingFilter(
        fields=(
            "id",
            "status",
            "assigned_to__last_name",
            "category",
            "created_at",
            "households_count",
            "user_modified",
            "household_unicef_id",
        )
    )

    @property
    def qs(self):
        return super().qs.annotate(
            household_unicef_id=Coalesce(
                "complaint_ticket_details__household__unicef_id",
                "sensitive_ticket_details__household__unicef_id",
                "sensitive_ticket_details__household__unicef_id",
                "individual_data_update_ticket_details__individual__household__unicef_id",
                "add_individual_ticket_details__household__unicef_id",
                "household_data_update_ticket_details__household__unicef_id",
                "delete_individual_ticket_details__individual__household__unicef_id",
                "system_flagging_ticket_details__golden_records_individual__household__unicef_id",
                "needs_adjudication_ticket_details__golden_records_individual__household__unicef_id",
            )
        )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(unicef_id__regex=rf"^(GRV-(0)+)?{value}$")
            for ticket_type, ticket_fields in self.SEARCH_TICKET_TYPES_LOOKUPS.items():
                for field, lookups in ticket_fields.items():
                    for lookup in lookups:
                        q_obj |= Q(**{f"{ticket_type}__{field}__{lookup}__startswith": value})

        return qs.filter(q_obj)

    def fsp_filter(self, qs, name, value):
        if value:
            q_obj = Q()
            for ticket_type, path_to_fsp in self.TICKET_TYPES_WITH_FSP:
                q_obj |= Q(**{f"{ticket_type}__{path_to_fsp}__full_name__istartswith": value})

            return qs.filter(q_obj)
        return qs

    def admin_filter(self, qs, name, value):
        if value:
            return qs.filter(admin2__in=[admin.id for admin in value])
        return qs

    def permissions_filter(self, qs, name, value):
        can_view_ex_sensitive_all = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE.value in value
        can_view_sensitive_all = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE.value in value
        can_view_ex_sensitive_creator = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR.value in value
        can_view_ex_sensitive_owner = Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER.value in value
        can_view_sensitive_creator = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR.value in value
        can_view_sensitive_owner = Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER.value in value

        # can view all
        if can_view_ex_sensitive_all and can_view_sensitive_all:
            return qs

        filters_1 = {}
        filters_1_exclude = {}
        filters_2 = {}
        filters_2_exclude = {}
        sensitive_category_filter = {"category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE}
        created_by_filter = {"created_by": self.request.user}
        assigned_to_filter = {"assigned_to": self.request.user}

        # can view one group full and potentially some of other group
        if can_view_ex_sensitive_all or can_view_sensitive_all:
            if can_view_sensitive_creator or can_view_ex_sensitive_creator:
                filters_1.update(created_by_filter)
            if can_view_sensitive_owner or can_view_ex_sensitive_owner:
                filters_2.update(assigned_to_filter)

            if can_view_ex_sensitive_all:
                return qs.filter(~Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_2))
            else:
                return qs.filter(Q(**sensitive_category_filter) | Q(**filters_1) | Q(**filters_1))

        else:
            # no full lists so only creator and/or owner lists
            if can_view_ex_sensitive_creator:
                filters_1.update(created_by_filter)
                if not can_view_sensitive_creator:
                    filters_1_exclude.update(sensitive_category_filter)
            if can_view_ex_sensitive_owner:
                filters_2.update(assigned_to_filter)
                if not can_view_sensitive_owner:
                    filters_2_exclude.update(sensitive_category_filter)
            if filters_1 or filters_2:
                return qs.filter(
                    Q(Q(**filters_1), ~Q(**filters_1_exclude)) | Q(Q(**filters_2), ~Q(**filters_2_exclude))
                )
            else:
                return GrievanceTicket.objects.none()


class ExistingGrievanceTicketFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    category = ChoiceFilter(field_name="category", choices=GrievanceTicket.CATEGORY_CHOICES)
    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    household = ModelChoiceFilter(queryset=Household.objects.all())
    individual = ModelChoiceFilter(queryset=Individual.objects.all())
    payment_record = ModelMultipleChoiceFilter(queryset=PaymentRecord.objects.all())
    permissions = MultipleChoiceFilter(choices=Permissions.choices(), method="permissions_filter")

    class Meta:
        fields = ("id",)
        model = GrievanceTicket

    order_by = OrderingFilter(fields=("id",))

    def prepare_ticket_filters(self, lookup, obj):
        types_and_lookups = GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS

        q_obj = Q()
        for ticket_type, lookup_objs in types_and_lookups.items():
            real_lookup = lookup_objs.get(lookup)
            if real_lookup:
                q_obj |= Q(**{f"{ticket_type}__{real_lookup}": obj})
        return q_obj

    def filter_queryset(self, queryset):
        cleaned_data = self.form.cleaned_data

        payment_record_objects = cleaned_data.pop("payment_record", None)
        household_object = cleaned_data.pop("household", None)
        individual_object = cleaned_data.pop("individual", None)
        # if any of these filters were passed in as wrong ids we need to return an empty queryset instead of completely ignore that filter value
        # as expected in OtherRelatedTickets.tsx component when passing random household id
        if (household_object is None and self.form.data.get("household")) or (
            payment_record_objects is None
            and self.form.data.get("payment_record")
            or (individual_object is None and self.form.data.get("individual"))
        ):
            return queryset.none()
        if household_object is None:
            queryset.model.objects.none()
        for name, value in cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '{}.{}' to return a QuerySet, but got a {} instead.".format(
                type(self).__name__,
                name,
                type(queryset).__name__,
            )

        if payment_record_objects:
            q_obj = Q()
            for payment_record in payment_record_objects:
                q_obj |= self.prepare_ticket_filters("payment_record", payment_record)
            queryset = queryset.filter(q_obj)
        if household_object:
            q_obj = self.prepare_ticket_filters("household", household_object)
            queryset = queryset.filter(q_obj)
        if individual_object:
            q_obj = self.prepare_ticket_filters("individual", individual_object)
            queryset = queryset.filter(q_obj)

        return queryset

    def permissions_filter(self, qs, name, value):
        return GrievanceTicketFilter.permissions_filter(self, qs, name, value)


class TicketNoteFilter(FilterSet):
    ticket = UUIDFilter(field_name="ticket", required=True)

    class Meta:
        fields = ("id",)
        model = TicketNote


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER),
    )
    household = graphene.Field(HouseholdNode)
    individual = graphene.Field(IndividualNode)
    payment_record = graphene.Field(PaymentRecordNode)
    related_tickets = graphene.List(lambda: GrievanceTicketNode)
    admin = graphene.String()

    @staticmethod
    def _search_for_lookup(grievance_ticket_obj, lookup_name):
        for field, lookups in GrievanceTicket.FIELD_TICKET_TYPES_LOOKUPS.items():
            extras_field = getattr(grievance_ticket_obj, field, None)
            if extras_field is None:
                continue
            real_lookup = lookup_name
            for lookup in lookups:
                if isinstance(lookup, dict):
                    tmp_lookup = lookup.get(lookup_name)
                    if tmp_lookup is not None:
                        real_lookup = tmp_lookup
                        break
            obj = nested_getattr(extras_field, real_lookup, None)
            if obj is not None:
                return obj

    @classmethod
    def check_node_permission(cls, info, object_instance):
        super().check_node_permission(info, object_instance)
        business_area = object_instance.business_area
        user = info.context.user

        if object_instance.category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER.value
        else:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER.value

        check_creator = object_instance.created_by == user and user.has_permission(creator_perm, business_area)
        check_assignee = object_instance.assigned_to == user and user.has_permission(owner_perm, business_area)
        if user.has_permission(perm, business_area) or check_creator or check_assignee:
            return True

        msg = "User is not active creator/assignee and does not have '{perm}' permission"
        logger.error(msg)
        raise GraphQLError(msg)

    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_related_tickets(grievance_ticket, info):
        return grievance_ticket.related_tickets

    def resolve_household(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "household")

    def resolve_individual(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "individual")

    def resolve_payment_record(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "payment_record")

    def resolve_admin(grievance_ticket, info):
        if grievance_ticket.admin2:
            return grievance_ticket.admin2.title
        return None


class TicketNoteNode(DjangoObjectType):
    class Meta:
        model = TicketNote
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketComplaintDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketComplaintDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketSensitiveDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSensitiveDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketIndividualDataUpdateDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_individual_data(self, info):
        individual_data = self.individual_data
        flex_fields = individual_data.get("flex_fields")
        if flex_fields:
            images_flex_fields_names = FlexibleAttribute.objects.filter(type=TYPE_IMAGE).values_list("name", flat=True)
            for name, value in flex_fields.items():
                if value and name in images_flex_fields_names:
                    try:
                        previous_value = value.get("previous_value", "")
                        if previous_value:
                            previous_value = default_storage.url(previous_value)
                        flex_fields[name]["previous_value"] = previous_value

                        current_value = value.get("value", "")
                        if current_value:
                            current_value = default_storage.url(current_value)
                        flex_fields[name]["value"] = current_value
                    except Exception:
                        pass
            individual_data["flex_fields"] = flex_fields

        documents_to_edit = individual_data.get("documents_to_edit")
        if documents_to_edit:
            for index, document in enumerate(documents_to_edit):
                previous_value = document.get("previous_value", {})
                if previous_value and previous_value.get("photo"):
                    previous_value["photoraw"] = previous_value["photo"]
                    previous_value["photo"] = default_storage.url(previous_value.get("photo"))
                    documents_to_edit[index]["previous_value"] = previous_value

                current_value = document.get("value", {})
                if current_value and current_value.get("photo"):
                    current_value["photoraw"] = current_value["photo"]
                    current_value["photo"] = default_storage.url(current_value.get("photo"))
                    documents_to_edit[index]["value"] = current_value
            individual_data["documents_to_edit"] = documents_to_edit

        documents = individual_data.get("documents")
        if documents:
            for index, document in enumerate(documents):
                current_value = document.get("value", {})
                if current_value and current_value.get("photo"):
                    current_value["photoraw"] = current_value["photo"]
                    current_value["photo"] = default_storage.url(current_value.get("photo"))
                    documents[index]["value"] = current_value
            individual_data["documents"] = documents

        return individual_data


class TicketAddIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketAddIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_individual_data(self, info):
        individual_data = self.individual_data
        flex_fields = individual_data.get("flex_fields")
        if flex_fields:
            images_flex_fields_names = FlexibleAttribute.objects.filter(type=TYPE_IMAGE).values_list("name", flat=True)
            for name, value in flex_fields.items():
                if value and name in images_flex_fields_names:
                    try:
                        if value:
                            flex_fields[name] = default_storage.url(value)
                        else:
                            flex_fields[name] = ""
                    except Exception:
                        pass
            individual_data["flex_fields"] = flex_fields

        documents = individual_data.get("documents")
        if documents:
            for index, document in enumerate(documents):
                if document and document["photo"]:
                    document["photoraw"] = document["photo"]
                    document["photo"] = default_storage.url(document["photo"])
                    documents[index] = document
            individual_data["documents"] = documents
        return individual_data


class TicketDeleteIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketDeleteIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketDeleteHouseholdDetailsNode(DjangoObjectType):
    household_data = Arg()

    class Meta:
        model = TicketDeleteHouseholdDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketHouseholdDataUpdateDetailsNode(DjangoObjectType):
    household_data = Arg()

    class Meta:
        model = TicketHouseholdDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNeedsAdjudicationDetailsExtraDataNode(graphene.ObjectType):
    golden_records = graphene.List(DeduplicationResultNode)
    possible_duplicate = graphene.List(DeduplicationResultNode)

    def resolve_golden_records(self, info):
        return encode_ids(self.golden_records, "Individual", "hit_id")

    def resolve_possible_duplicate(self, info):
        return encode_ids(self.possible_duplicate, "Individual", "hit_id")


class TicketNeedsAdjudicationDetailsNode(DjangoObjectType):
    has_duplicated_document = graphene.Boolean()
    extra_data = graphene.Field(TicketNeedsAdjudicationDetailsExtraDataNode)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_extra_data(parent, info):
        golden_records = parent.extra_data.get("golden_records")
        possible_duplicate = parent.extra_data.get("possible_duplicate")
        return TicketNeedsAdjudicationDetailsExtraDataNode(golden_records, possible_duplicate)


class TicketSystemFlaggingDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSystemFlaggingDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPaymentVerificationDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketPaymentVerificationDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPositiveFeedbackDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketPositiveFeedbackDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNegativeFeedbackDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketNegativeFeedbackDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketReferralDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketReferralDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class IssueTypesObject(graphene.ObjectType):
    category = graphene.String()
    label = graphene.String()
    sub_categories = graphene.List(ChoiceObject)

    def resolve_sub_categories(self, info):
        return [{"name": value, "value": key} for key, value in self.get("sub_categories").items()]


class AddIndividualFiledObjectType(graphene.ObjectType):
    name = graphene.String()
    label = graphene.String()
    required = graphene.Boolean()
    type = graphene.String()
    flex_field = graphene.Boolean()


class ChartGrievanceTicketsNode(ChartDatasetNode):
    total_number_of_grievances = graphene.Int()
    total_number_of_feedback = graphene.Int()
    total_number_of_open_sensitive = graphene.Int()


class Query(graphene.ObjectType):
    grievance_ticket = relay.Node.Field(GrievanceTicketNode)
    all_grievance_ticket = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        permission_classes=(
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER),
        ),
    )
    existing_grievance_tickets = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=ExistingGrievanceTicketFilter,
        permission_classes=(
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER),
        ),
    )
    all_ticket_notes = DjangoPermissionFilterConnectionField(
        TicketNoteNode,
        filterset_class=TicketNoteFilter,
    )
    chart_grievances = graphene.Field(
        ChartGrievanceTicketsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        administrative_area=graphene.String(required=False),
    )
    all_add_individuals_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    all_edit_household_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    grievance_ticket_status_choices = graphene.List(ChoiceObject)
    grievance_ticket_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_manual_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_issue_type_choices = graphene.List(IssueTypesObject)

    def resolve_all_grievance_ticket(self, info, **kwargs):
        return GrievanceTicket.objects.select_related("assigned_to", "created_by")

    def resolve_grievance_ticket_status_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.STATUS_CHOICES)

    def resolve_grievance_ticket_category_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.CATEGORY_CHOICES)

    def resolve_grievance_ticket_manual_category_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in GrievanceTicket.CATEGORY_CHOICES
            if value in GrievanceTicket.MANUAL_CATEGORIES
        ]

    def resolve_grievance_ticket_all_category_choices(self, info, **kwargs):
        return [{"name": name, "value": value} for value, name in GrievanceTicket.CATEGORY_CHOICES]

    def resolve_grievance_ticket_issue_type_choices(self, info, **kwargs):
        categories = choices_to_dict(GrievanceTicket.CATEGORY_CHOICES)
        return [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ]

    def resolve_all_add_individuals_fields_attributes(self, info, **kwargs):
        ACCEPTABLE_FIELDS = [
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "disability",
            "work_status",
            "enrolled_in_nutrition_programme",
            "administration_of_rutf",
            "pregnant",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "who_answers_phone",
            "who_answers_alt_phone",
        ]

        all_options = (
            [
                x
                for x in CORE_FIELDS_ATTRIBUTES
                if x.get("associated_with") == _INDIVIDUAL and x.get("name") in ACCEPTABLE_FIELDS
            ]
            + list(KOBO_ONLY_INDIVIDUAL_FIELDS.values())
            + list(FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL))
        )

        return sort_by_attr(all_options, "label.English(EN)")

    def resolve_all_edit_household_fields_attributes(self, info, **kwargs):
        ACCEPTABLE_FIELDS = [
            "status",
            "consent",
            "consent_sharing",
            "residence_status",
            "country_origin",
            "country",
            "size",
            "address",
            "admin_area_title",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "returnee",
            "fchild_hoh",
            "child_hoh",
            "start",
            "end",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
            "registration_method",
            "collect_individual_data",
            "currency",
            "unhcr_id",
        ]

        # yield from FlexibleAttribute.objects.order_by("name").all()
        all_options = [
            x
            for x in HOUSEHOLD_EDIT_ONLY_FIELDS + CORE_FIELDS_ATTRIBUTES
            if x.get("associated_with") == _HOUSEHOLD and x.get("name") in ACCEPTABLE_FIELDS
        ] + list(FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD))

        return sort_by_attr(all_options, "label.English(EN)")

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_grievances(self, info, business_area_slug, year, **kwargs):
        grievance_tickets = chart_get_filtered_qs(
            GrievanceTicket,
            year,
            business_area_slug_filter={"business_area__slug": business_area_slug},
        )

        filters = chart_filters_decoder(kwargs)
        if filters.get("administrative_area") is not None:
            from hct_mis_api.apps.core.models import AdminArea

            try:
                grievance_tickets = grievance_tickets.filter(
                    admin=AdminArea.objects.get(id=filters.get("administrative_area")).title
                )
            except AdminArea.DoesNotExist:
                pass

        grievance_status_labels = [
            "Resolved",
            "Unresolved",
            "Unresolved for longer than 30 days",
            "Unresolved for longer than 60 days",
        ]

        days_30_from_now = datetime.date.today() - datetime.timedelta(days=30)
        days_60_from_now = datetime.date.today() - datetime.timedelta(days=60)

        feedback_categories = [GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK, GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK]
        all_open_tickets = grievance_tickets.filter(~Q(status=GrievanceTicket.STATUS_CLOSED))
        all_closed_tickets = grievance_tickets.filter(status=GrievanceTicket.STATUS_CLOSED)

        datasets = [
            {
                "data": [
                    all_closed_tickets.count(),  # Resolved
                    all_open_tickets.filter(
                        created_at__gte=days_30_from_now,
                    ).count(),  # Unresolved less than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_30_from_now,
                        created_at__gte=days_60_from_now,
                    ).count(),  # Unresolved for longer than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_60_from_now
                    ).count(),  # Unresolved for longer than 60 days
                ]
            },
        ]
        return {
            "labels": grievance_status_labels,
            "datasets": datasets,
            "total_number_of_grievances": grievance_tickets.exclude(category__in=feedback_categories).count(),
            "total_number_of_feedback": grievance_tickets.filter(category__in=feedback_categories).count(),
            "total_number_of_open_sensitive": all_open_tickets.filter(
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            ).count(),
        }
