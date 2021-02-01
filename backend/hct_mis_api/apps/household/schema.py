from django.db.models import Prefetch, Q, Sum
from django.db.models.functions import Lower

import graphene
from django_filters import (
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.countries import Countries
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import AgeRangeFilter, DateRangeFilter, IntegerRangeFilter
from hct_mis_api.apps.core.models import AdminArea
from hct_mis_api.apps.core.schema import ChoiceObject, AdminAreaNode
from hct_mis_api.apps.core.utils import (
    CustomOrderingFilter,
    decode_id_string,
    encode_ids,
    to_choice_object,
    chart_get_filtered_qs,
    sum_lists
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    IDENTIFICATION_TYPE_CHOICE,
    INDIVIDUAL_HOUSEHOLD_STATUS,
    MARITAL_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    ROLE_NO_ROLE,
    SEX_CHOICE,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.registration_datahub.schema import DeduplicationResultNode
from hct_mis_api.apps.utils.schema import ChartDatasetNode, ChartDetailedDatasetsNode, SectionTotalNode


INDIVIDUALS_CHART_LABELS = [
    'Females 0-5',
    'Females 6-11',
    'Females 12-17',
    'Females 18-59',
    'Females 60+',
    'Males 0-5',
    'Males 6-11',
    'Males 12-17',
    'Males 18-59',
    'Males 60+'
]


class HouseholdFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(
        field_name="admin_area", queryset=AdminArea.objects.filter(level=2)
    )

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact"],
            "country_origin": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "head_of_household__full_name": ["exact", "icontains"],
            "size": ["range", "lte", "gte"],
            "admin_area": ["exact"],
            "target_populations": ["exact"],
            "programs": ["exact"],
            "residence_status": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "age",
            "sex",
            "household__id",
            "id",
            "unicef_id",
            "household_ca_id",
            "size",
            Lower("head_of_household__full_name"),
            Lower("admin_area__title"),
            "residence_status",
            Lower("registration_data_import__name"),
            "total_cash",
            "last_registration_date",
            "first_registration_date",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(head_of_household__given_name__icontains=value)
            q_obj |= Q(head_of_household__family_name__icontains=value)
            q_obj |= Q(unicef_id__icontains=value)
            q_obj |= Q(id__icontains=value)
        return qs.filter(q_obj)


class IndividualFilter(FilterSet):
    business_area = CharFilter(
        field_name="household__business_area__slug",
    )
    age = AgeRangeFilter(field_name="birth_date")
    sex = MultipleChoiceFilter(field_name="sex", choices=SEX_CHOICE)
    programs = ModelMultipleChoiceFilter(field_name="household__programs", queryset=Program.objects.all())
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(
        field_name="household__admin_area", queryset=AdminArea.objects.filter(level=2)
    )
    status = MultipleChoiceFilter(field_name="status", choices=INDIVIDUAL_HOUSEHOLD_STATUS)
    excluded_id = CharFilter(method="filter_excluded_id")

    class Meta:
        model = Individual
        fields = {
            "household__id": ["exact"],
            "programs": ["exact"],
            "business_area": ["exact"],
            "full_name": ["exact", "icontains"],
            "age": ["range", "lte", "gte"],
            "sex": ["exact"],
            "household__admin_area": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            "unicef_id",
            Lower("full_name"),
            "household__id",
            "birth_date",
            "sex",
            "relationship",
            Lower("household__admin_area__title"),
            "last_registration_date",
            "first_registration_date",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(household__admin_area__title__icontains=value)
            q_obj |= Q(unicef_id__icontains=value)
            q_obj |= Q(household__id__icontains=value)
            q_obj |= Q(household__unicef_id=value)
            q_obj |= Q(full_name__icontains=value)
        return qs.filter(q_obj)

    def filter_excluded_id(self, qs, name, value):
        return qs.exclude(id=decode_id_string(value))


class DocumentTypeNode(DjangoObjectType):
    country = graphene.String(description="Country name")

    def resolve_country(parent, info):
        return parent.country.name

    class Meta:
        model = DocumentType


class IndividualIdentityNode(DjangoObjectType):
    type = graphene.String(description="Agency type")

    def resolve_type(parent, info):
        return parent.agency.type

    class Meta:
        model = IndividualIdentity


class DocumentNode(DjangoObjectType):
    class Meta:
        model = Document
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FlexFieldsScalar(graphene.Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class ExtendedHouseHoldConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    individuals_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)

    def resolve_individuals_count(root, info, **kwargs):
        return root.iterable.aggregate(sum=Sum("size")).get("sum")


# FIXME: This need to be changed to HouseholdSelectionNode
class HouseholdSelection(DjangoObjectType):
    class Meta:
        model = HouseholdSelection


class HouseholdNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER),
    )

    total_cash_received = graphene.Decimal()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    flex_fields = FlexFieldsScalar()
    selection = graphene.Field(HouseholdSelection)
    sanction_list_possible_match = graphene.Boolean()
    has_duplicates = graphene.Boolean(description="Mark household if any of individuals has Duplicate status")
    consent_sharing = graphene.List(graphene.String)
    admin1 = graphene.Field(AdminAreaNode)
    admin2 = graphene.Field(AdminAreaNode)

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_origin(parent, info):
        return parent.country_origin.name

    def resolve_selection(parent, info):
        selection = parent.selections.first()
        return selection

    def resolve_individuals(parent, info):
        individuals_ids = list(parent.individuals.values_list("id", flat=True))
        collectors_ids = list(parent.representatives.values_list("id", flat=True))
        ids = list(set(individuals_ids + collectors_ids))
        return Individual.objects.filter(id__in=ids).prefetch_related(
            Prefetch(
                "households_and_roles",
                queryset=IndividualRoleInHousehold.objects.filter(household=parent.id),
            )
        )

    def resolve_has_duplicates(parent, info):
        return parent.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()

    @classmethod
    def check_node_permission(cls, info, object_instance):
        super().check_node_permission(info, object_instance)
        user = info.context.user

        # if user doesn't have permission to view all households, we check based on their grievance tickets
        if not user.has_permission(Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value, object_instance.business_area):
            grievance_tickets = GrievanceTicket.objects.filter(
                complaint_ticket_details__in=object_instance.complaint_ticket_details.all()
            )
            cls.check_creator_or_owner_permission(
                info,
                object_instance,
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS.value,
                any(user_ticket in user.created_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR.value,
                any(user_ticket in user.assigned_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER.value,
            )

    # I don't think this is needed because it would skip check_node_permission call
    # @classmethod
    # def get_node(cls, info, id):
    #     # This will skip permission check from BaseNodePermissionMixin, check if okay
    #     queryset = cls.get_queryset(cls._meta.model.all_objects, info)
    #     try:
    #         return queryset.get(pk=id)
    #     except cls._meta.model.DoesNotExist:
    #         return None

    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedHouseHoldConnection


class IndividualRoleInHouseholdNode(DjangoObjectType):
    class Meta:
        model = IndividualRoleInHousehold


class IndividualNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER),
    )

    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    flex_fields = FlexFieldsScalar()
    deduplication_golden_record_results = graphene.List(DeduplicationResultNode)
    deduplication_batch_results = graphene.List(DeduplicationResultNode)
    observed_disability = graphene.List(graphene.String)
    relationship = graphene.Enum(
        "IndividualRelationship",
        [(x[0], x[0]) for x in RELATIONSHIP_CHOICE],
    )

    def resolve_role(parent, info):
        role = parent.households_and_roles.first()
        if role is not None:
            return role.role
        return ROLE_NO_ROLE

    def resolve_deduplication_golden_record_results(parent, info):
        key = "duplicates" if parent.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = parent.deduplication_golden_record_results.get(key, {})
        return encode_ids(results, "Individual", "hit_id")

    def resolve_deduplication_batch_results(parent, info):
        key = "duplicates" if parent.deduplication_batch_status == DUPLICATE_IN_BATCH else "possible_duplicates"
        results = parent.deduplication_batch_results.get(key, {})
        return encode_ids(results, "ImportedIndividual", "hit_id")

    def resolve_relationship(parent, info):
        # custom resolver so when relationship value is empty string, query does not break (since empty string is not one of enum choices, we need to return None)
        if not parent.relationship:
            return None
        return parent.relationship

    @classmethod
    def check_node_permission(cls, info, object_instance):
        super().check_node_permission(info, object_instance)
        user = info.context.user
        # if user can't simply view all individuals, we check if they can do it because of grievance
        if not user.has_permission(
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS.value, object_instance.business_area
        ):
            grievance_tickets = GrievanceTicket.objects.filter(
                complaint_ticket_details__in=object_instance.complaint_ticket_details.all()
            )
            cls.check_creator_or_owner_permission(
                info,
                object_instance,
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS.value,
                any(user_ticket in user.created_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR.value,
                any(user_ticket in user.assigned_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER.value,
            )

    # I don't think this is needed because it would skip check_node_permission call
    # @classmethod
    # def get_node(cls, info, id):
    #     queryset = cls.get_queryset(cls._meta.model.all_objects, info)
    #     try:
    #         return queryset.get(pk=id)
    #     except cls._meta.model.DoesNotExist:
    #         return None

    class Meta:
        model = Individual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ChartAllHouseHoldsReached(ChartDatasetNode):
    female_age_group_0_5_count = graphene.Int()
    female_age_group_6_11_count = graphene.Int()
    female_age_group_12_17_count = graphene.Int()
    female_age_group_18_59_count = graphene.Int()
    female_age_group_60_count = graphene.Int()
    male_age_group_0_5_count = graphene.Int()
    male_age_group_6_11_count = graphene.Int()
    male_age_group_12_17_count = graphene.Int()
    male_age_group_18_59_count = graphene.Int()
    male_age_group_60_count = graphene.Int()


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        filterset_class=HouseholdFilter,
        permission_classes=(hopePermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST),),
    )
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoPermissionFilterConnectionField(
        IndividualNode,
        filterset_class=IndividualFilter,
        permission_classes=(hopePermissionClass(Permissions.POPULATION_VIEW_INDIVIDUALS_LIST),),
    )
    chart_all_individuals_reached = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    section_households_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    section_individuals_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    section_child_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    chart_individuals_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    chart_individuals_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )

    residence_status_choices = graphene.List(ChoiceObject)
    sex_choices = graphene.List(ChoiceObject)
    marital_status_choices = graphene.List(ChoiceObject)
    relationship_choices = graphene.List(ChoiceObject)
    role_choices = graphene.List(ChoiceObject)
    document_type_choices = graphene.List(ChoiceObject)
    countries_choices = graphene.List(ChoiceObject)

    def resolve_all_households(self, info, **kwargs):
        return Household.objects.annotate(total_cash=Sum("payment_records__delivered_quantity")).order_by("created_at")

    def resolve_residence_status_choices(self, info, **kwargs):
        return to_choice_object(RESIDENCE_STATUS_CHOICE)

    def resolve_sex_choices(self, info, **kwargs):
        return to_choice_object(SEX_CHOICE)

    def resolve_marital_status_choices(self, info, **kwargs):
        return to_choice_object(MARITAL_STATUS_CHOICE)

    def resolve_relationship_choices(self, info, **kwargs):
        return to_choice_object(RELATIONSHIP_CHOICE)

    def resolve_role_choices(self, info, **kwargs):
        return to_choice_object(ROLE_CHOICE)

    def resolve_document_type_choices(self, info, **kwargs):
        return to_choice_object(IDENTIFICATION_TYPE_CHOICE)

    def resolve_countries_choices(self, info, **kwargs):
        return to_choice_object([(alpha3, label) for (label, alpha2, alpha3) in Countries.COUNTRIES])

    # def resolve_chart_all_individuals_reached(self, info, business_area_slug, year, **kwargs):
    #     households_qs = chart_get_filtered_qs(Household, business_area_slug, year)

    def resolve_section_households_reached(self, info, business_area_slug, year, **kwargs):
        payment_verifications_qs = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={'payment_record__business_area__slug': business_area_slug},
            additional_filters={"status": PaymentVerification.STATUS_RECEIVED},
        )
        return {
            "total": payment_verifications_qs.values_list('payment_record__household', flat=True).distinct().count()
        }

    def resolve_section_individuals_reached(self, info, business_area_slug, year, **kwargs):
        payment_verifications_qs = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={'payment_record__business_area__slug': business_area_slug},
            additional_filters={"status": PaymentVerification.STATUS_RECEIVED},
        )
        reached_households = set([pv.payment_record.household for pv in payment_verifications_qs])
        return {"total": sum([hh.individuals.all().count() for hh in reached_households])}

    def resolve_section_child_reached(self, info, business_area_slug, year, **kwargs):
        payment_verifications_qs = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={'payment_record__business_area__slug': business_area_slug},
            additional_filters={"status": PaymentVerification.STATUS_RECEIVED},
        )

        households_child_params = [
            'payment_record__household__female_age_group_0_5_count',
            'payment_record__household__female_age_group_0_5_disabled_count',
            'payment_record__household__female_age_group_6_11_count',
            'payment_record__household__female_age_group_6_11_disabled_count',
            'payment_record__household__female_age_group_12_17_count',
            'payment_record__household__female_age_group_12_17_disabled_count',
        ]

        households_child_values = payment_verifications_qs.values_list(
            *households_child_params
        ).distinct()

        return {"total": sum(sum_lists(households_child_values, len(households_child_params)))}

    def resolve_chart_individuals_reached_by_age_and_gender(self, info, business_area_slug, year, **kwargs):
        payment_verifications_qs = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={'payment_record__business_area__slug': business_area_slug},
            additional_filters={"status": PaymentVerification.STATUS_RECEIVED},
        )
        households_params = [
            'payment_record__household__female_age_group_0_5_count',
            'payment_record__household__female_age_group_0_5_disabled_count',
            'payment_record__household__female_age_group_6_11_count',
            'payment_record__household__female_age_group_6_11_disabled_count',
            'payment_record__household__female_age_group_12_17_count',
            'payment_record__household__female_age_group_12_17_disabled_count',
            'payment_record__household__female_age_group_18_59_count',
            'payment_record__household__female_age_group_18_59_disabled_count',
            'payment_record__household__female_age_group_60_count',
            'payment_record__household__female_age_group_60_disabled_count',
            'payment_record__household__male_age_group_0_5_count',
            'payment_record__household__male_age_group_0_5_disabled_count',
            'payment_record__household__male_age_group_6_11_count',
            'payment_record__household__male_age_group_6_11_disabled_count',
            'payment_record__household__male_age_group_12_17_count',
            'payment_record__household__male_age_group_12_17_disabled_count',
            'payment_record__household__male_age_group_18_59_count',
            'payment_record__household__male_age_group_18_59_disabled_count',
            'payment_record__household__male_age_group_60_count',
            'payment_record__household__male_age_group_60_disabled_count',
        ]

        households_values = payment_verifications_qs.values_list(
            *households_params
        ).distinct()

        return {
            'labels': INDIVIDUALS_CHART_LABELS,
            'datasets': [{'data': sum_lists(households_values, len(households_params))}]
        }

    def resolve_chart_individuals_with_disability_reached_by_age(self, info, business_area_slug, year, **kwargs):
        payment_verifications_qs = chart_get_filtered_qs(
            PaymentVerification,
            year,
            business_area_slug_filter={'payment_record__business_area__slug': business_area_slug},
            additional_filters={"status": PaymentVerification.STATUS_RECEIVED},
        )
        households_params_with_disability = [
            'payment_record__household__female_age_group_0_5_disabled_count',
            'payment_record__household__female_age_group_6_11_disabled_count',
            'payment_record__household__female_age_group_12_17_disabled_count',
            'payment_record__household__female_age_group_18_59_disabled_count',
            'payment_record__household__female_age_group_60_disabled_count',
            'payment_record__household__male_age_group_0_5_disabled_count',
            'payment_record__household__male_age_group_6_11_disabled_count',
            'payment_record__household__male_age_group_12_17_disabled_count',
            'payment_record__household__male_age_group_18_59_disabled_count',
            'payment_record__household__male_age_group_60_disabled_count',
        ]
        households_params_without_disability = [
            'payment_record__household__female_age_group_0_5_count',
            'payment_record__household__female_age_group_6_11_count',
            'payment_record__household__female_age_group_12_17_count',
            'payment_record__household__female_age_group_18_59_count',
            'payment_record__household__female_age_group_60_count',
            'payment_record__household__male_age_group_0_5_count',
            'payment_record__household__male_age_group_6_11_count',
            'payment_record__household__male_age_group_12_17_count',
            'payment_record__household__male_age_group_18_59_count',
            'payment_record__household__male_age_group_60_count',
        ]

        households_with_disability_values = payment_verifications_qs.values_list(
            *households_params_with_disability
        ).distinct()

        households_without_disability_values = payment_verifications_qs.values_list(
            *households_params_without_disability
        ).distinct()

        datasets = [
            {
                "label": 'with disability',
                "data": sum_lists(households_with_disability_values, len(households_params_with_disability))
            },
            {
                "label": 'without disability',
                "data": sum_lists(households_without_disability_values, len(households_params_without_disability))
            }
        ]

        return {
            'labels': INDIVIDUALS_CHART_LABELS,
            'datasets': datasets
        }

