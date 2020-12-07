import graphene
from django.db import models
from django.db.models import Q
from django.db.models.functions import Coalesce
from django_filters import (
    FilterSet,
    CharFilter,
    ModelMultipleChoiceFilter,
    OrderingFilter,
    TypedMultipleChoiceFilter,
    ChoiceFilter,
    ModelChoiceFilter,
    UUIDFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType

from account.permissions import BaseNodePermissionMixin, DjangoPermissionFilterConnectionField
from core.core_fields_attributes import CORE_FIELDS_ATTRIBUTES, _INDIVIDUAL, _HOUSEHOLD, KOBO_COLLECTOR_FIELD
from core.extended_connection import ExtendedConnection
from core.filters import DateTimeRangeFilter
from core.models import AdminArea, FlexibleAttribute
from core.schema import ChoiceObject, FieldAttributeNode
from core.utils import to_choice_object, choices_to_dict
from grievance.models import (
    GrievanceTicket,
    TicketNote,
    TicketSensitiveDetails,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketAddIndividualDetails,
    TicketHouseholdDataUpdateDetails,
)
from household.models import Household, Individual
from household.schema import HouseholdNode, IndividualNode
from payment.models import ServiceProvider, PaymentRecord
from payment.schema import PaymentRecordNode
from utils.schema import Arg


class GrievanceTicketFilter(FilterSet):
    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
            "household": ("id",),
        },
        "sensitive_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
            "household": ("id",),
        },
        "individual_data_update_ticket_details": {
            "individual": ("full_name", "id", "phone_no", "phone_no_alternative"),
        },
        "add_individual_ticket_details": {"household": ("id",)},
    }
    TICKET_TYPES_WITH_FSP = ("complaint_ticket_details", "sensitive_ticket_details")

    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = TypedMultipleChoiceFilter(field_name="status", choices=GrievanceTicket.STATUS_CHOICES, coerce=int)
    fsp = ModelMultipleChoiceFilter(method="fsp_filter", queryset=ServiceProvider.objects.all())
    admin = ModelMultipleChoiceFilter(
        field_name="admin", method="admin_filter", queryset=AdminArea.objects.filter(admin_area_type__admin_level=2)
    )
    created_at_range = DateTimeRangeFilter(field_name="created_at")

    class Meta:
        fields = {
            "id": ["exact", "icontains"],
            "category": ["exact"],
            "area": ["exact", "icontains"],
            "assigned_to": ["exact"],
        }
        model = GrievanceTicket

    order_by = OrderingFilter(
        fields=(
            "id",
            "status",
            "assigned_to__first_name",
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
            )
        )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__icontains=value)
            for ticket_type, ticket_fields in self.SEARCH_TICKET_TYPES_LOOKUPS.items():
                for field, lookups in ticket_fields.items():
                    for lookup in lookups:
                        q_obj |= Q(**{f"{ticket_type}__{field}__{lookup}__icontains": value})

        return qs.filter(q_obj)

    def fsp_filter(self, qs, name, value):
        if value:
            q_obj = Q()
            for ticket_type in self.TICKET_TYPES_WITH_FSP:
                q_obj |= Q(**{f"{ticket_type}__payment_record__service_provider__in": value})

            return qs.filter(q_obj)
        return qs

    def admin_filter(self, qs, name, value):
        if value:
            return qs.filter(admin__in=[admin.title for admin in value])
        return qs


class ExistingGrievanceTicketFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    category = ChoiceFilter(field_name="category", choices=GrievanceTicket.CATEGORY_CHOICES)
    issue_type = ChoiceFilter(field_name="issue_type", choices=GrievanceTicket.ALL_ISSUE_TYPES)
    household = ModelChoiceFilter(queryset=Household.objects.all())
    individual = ModelChoiceFilter(queryset=Individual.objects.all())
    payment_record = ModelMultipleChoiceFilter(queryset=PaymentRecord.objects.all())

    class Meta:
        fields = ("id",)
        model = GrievanceTicket

    order_by = OrderingFilter(fields=("id",))

    def prepare_ticket_filters(self, lookup, obj):
        types_and_lookups = GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS
        ticket_types = types_and_lookups.keys()

        q_obj = Q()
        for ticket_type in ticket_types:
            has_lookup = lookup in types_and_lookups[ticket_type]
            real_lookup = lookup
            if not has_lookup:
                for lookup_obj in types_and_lookups[ticket_type]:
                    if isinstance(lookup_obj, dict):
                        real_lookup = lookup_obj.get(lookup)
                        break
            if has_lookup:
                q_obj |= Q(**{f"{ticket_type}__{real_lookup}": obj})

        return q_obj

    def filter_queryset(self, queryset):
        cleaned_data = self.form.cleaned_data

        payment_record_objects = cleaned_data.pop("payment_record", None)
        household_object = cleaned_data.pop("household", None)
        individual_object = cleaned_data.pop("individual", None)
        if household_object is None:
            queryset.model.objects.none()
        for name, value in cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '%s.%s' to return a QuerySet, but got a %s instead." % (
                type(self).__name__,
                name,
                type(queryset).__name__,
            )

        if payment_record_objects:
            q_obj = Q()
            for payment_record in payment_record_objects:
                q_obj |= self.prepare_ticket_filters("payment_record", payment_record)
            return queryset.filter(q_obj)
        elif household_object:
            q_obj = self.prepare_ticket_filters("household", household_object)
            return queryset.filter(q_obj)
        elif individual_object:
            q_obj = self.prepare_ticket_filters("individual", individual_object)
            return queryset.filter(q_obj)

        return queryset


class TicketNoteFilter(FilterSet):
    ticket = UUIDFilter(field_name="ticket", required=True)

    class Meta:
        fields = ("id",)
        model = TicketNote


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    household = graphene.Field(HouseholdNode)
    individual = graphene.Field(IndividualNode)
    payment_record = graphene.Field(PaymentRecordNode)
    related_tickets = graphene.List(lambda: GrievanceTicketNode)

    @staticmethod
    def _search_for_lookup(grievance_ticket_obj, lookup_name):
        for field, lookups in GrievanceTicket.FIELD_TICKET_TYPES_LOOKUPS.items():
            extras_field = getattr(grievance_ticket_obj, field, {})
            obj = getattr(extras_field, lookup_name, None)
            if obj is not None:
                return obj

    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_household(grievance_ticket, info):
        return grievance_ticket.related_tickets

    def resolve_household(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "household")

    def resolve_individual(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "individual")

    def resolve_payment_record(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "payment_record")


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


class TicketAddIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketAddIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketDeleteIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketDeleteIndividualDetails
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


class Query(graphene.ObjectType):
    grievance_ticket = relay.Node.Field(GrievanceTicketNode)
    all_grievance_ticket = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),)
    )
    existing_grievance_tickets = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=ExistingGrievanceTicketFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),))
    )
    all_ticket_notes = DjangoPermissionFilterConnectionField(
        TicketNoteNode,
        filterset_class=TicketNoteFilter,
    )
    all_add_individuals_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    all_edit_household_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    grievance_ticket_status_choices = graphene.List(ChoiceObject)
    grievance_ticket_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_manual_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_issue_type_choices = graphene.List(IssueTypesObject)

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

        yield from [
            x
            for x in CORE_FIELDS_ATTRIBUTES
            if x.get("associated_with") == _INDIVIDUAL and x.get("name") in ACCEPTABLE_FIELDS
        ]
        yield KOBO_COLLECTOR_FIELD.get("role_i_c")
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
        ).order_by("name")

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
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_adults_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_adults_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_adults_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_adults_disabled_count",
            "returnee",
            "fchild_hoh",
            "child_hoh",
            "start",
            "end",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
        ]

        # yield from FlexibleAttribute.objects.order_by("name").all()
        yield from [
            x
            for x in CORE_FIELDS_ATTRIBUTES
            if x.get("associated_with") == _HOUSEHOLD and x.get("name") in ACCEPTABLE_FIELDS
        ]
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
        ).order_by("name")