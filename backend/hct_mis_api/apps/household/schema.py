import re

from django.db.models import Prefetch, Q, Sum
from django.db.models.functions import Coalesce, Lower

import graphene
from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.core.countries import Countries
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import (
    AgeRangeFilter,
    DateRangeFilter,
    IntegerRangeFilter,
)
from hct_mis_api.apps.core.models import AdminArea, FlexibleAttribute
from hct_mis_api.apps.core.schema import (
    AdminAreaNode,
    ChoiceObject,
    FieldAttributeNode,
    _custom_dict_or_attr_resolver,
)
from hct_mis_api.apps.core.utils import (
    CustomOrderingFilter,
    chart_filters_decoder,
    chart_permission_decorator,
    decode_id_string,
    encode_ids,
    get_model_choices_fields,
    resolve_flex_fields_choices_to_string,
    sum_lists_with_values,
    to_choice_object,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import (
    AGENCY_TYPE_CHOICES,
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    IDENTIFICATION_TYPE_CHOICE,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    MARITAL_STATUS_CHOICE,
    NEEDS_ADJUDICATION,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    ROLE_NO_ROLE,
    SANCTION_LIST_CONFIRMED_MATCH,
    SANCTION_LIST_POSSIBLE_MATCH,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    STATUS_ACTIVE,
    STATUS_DUPLICATE,
    STATUS_WITHDRAWN,
    WORK_STATUS_CHOICE,
    Agency,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.utils import get_payment_records_for_dashboard
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_datahub.schema import DeduplicationResultNode
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    FlexFieldsScalar,
    SectionTotalNode,
)

INDIVIDUALS_CHART_LABELS = [
    "Females 0-5",
    "Females 6-11",
    "Females 12-17",
    "Females 18-59",
    "Females 60+",
    "Males 0-5",
    "Males 6-11",
    "Males 12-17",
    "Males 18-59",
    "Males 60+",
]


class HouseholdFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")
    country_origin = CharFilter(field_name="country_origin", lookup_expr=["exact", "startswith"])
    head_of_household__full_name = CharFilter(
        field_name="head_of_household__full_name", lookup_expr=["exact", "startswith"]
    )
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(field_name="admin_area", queryset=AdminArea.objects.filter(level=2))
    withdrawn = BooleanFilter(field_name="withdrawn")

    class Meta:
        model = Household
        fields = [
            "business_area",
            "country_origin",
            "address",
            "head_of_household__full_name",
            "size",
            "admin_area",
            "target_populations",
            "programs",
            "residence_status",
            "withdrawn",
        ]

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
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            inner_query = Q()
            inner_query |= Q(head_of_household__full_name__startswith=value)
            inner_query |= Q(head_of_household__given_name__startswith=value)
            inner_query |= Q(head_of_household__middle_name__startswith=value)
            inner_query |= Q(head_of_household__family_name__startswith=value)
            inner_query |= Q(unicef_id__startswith=value)
            inner_query |= Q(unicef_id__endswith=value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()


class IndividualFilter(FilterSet):
    business_area = CharFilter(
        field_name="business_area__slug",
    )
    age = AgeRangeFilter(field_name="birth_date", lookup_expr=["range", "lte", "gte"])
    sex = MultipleChoiceFilter(field_name="sex", choices=SEX_CHOICE)
    programs = ModelMultipleChoiceFilter(field_name="household__programs", queryset=Program.objects.all())
    search = CharFilter(method="search_filter")
    last_registration_date = DateRangeFilter(field_name="last_registration_date")
    admin2 = ModelMultipleChoiceFilter(field_name="household__admin_area", queryset=AdminArea.objects.filter(level=2))
    status = MultipleChoiceFilter(choices=INDIVIDUAL_STATUS_CHOICES, method="status_filter")
    excluded_id = CharFilter(method="filter_excluded_id")
    withdrawn = BooleanFilter(field_name="withdrawn")
    full_name = CharFilter(field_name="full_name", lookup_expr=["exact", "startswith", "endswith"])
    flags = MultipleChoiceFilter(choices=INDIVIDUAL_FLAGS_CHOICES, method="flags_filter")

    class Meta:
        model = Individual
        fields = [
            "household__id",
            "programs",
            "business_area",
            "full_name",
            "age",
            "sex",
            "household__admin_area",
            "withdrawn",
        ]

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            "unicef_id",
            Lower("full_name"),
            "household__id",
            "household__unicef_id",
            "birth_date",
            "sex",
            "relationship",
            Lower("household__admin_area__title"),
            "last_registration_date",
            "first_registration_date",
        )
    )

    def flags_filter(self, qs, name, value):
        q_obj = Q()
        if NEEDS_ADJUDICATION in value:
            q_obj |= Q(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        if DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if SANCTION_LIST_POSSIBLE_MATCH in value:
            q_obj |= Q(sanction_list_possible_match=True, sanction_list_confirmed_match=False)
        if SANCTION_LIST_CONFIRMED_MATCH in value:
            q_obj |= Q(sanction_list_confirmed_match=True)

        return qs.filter(q_obj)

    def search_filter(self, qs, name, value):
        if re.match(r"([\"\']).+\1", value):
            values = [value.replace('"', "").strip()]
        else:
            values = value.split(" ")
        q_obj = Q()
        for value in values:
            inner_query = Q()
            q_obj |= Q(household__admin_area__title__startswith=value)
            q_obj |= Q(unicef_id__startswith=value)
            q_obj |= Q(unicef_id__endswith=value)
            q_obj |= Q(household__unicef_id__startswith=value)
            q_obj |= Q(full_name__startswith=value)
            q_obj |= Q(given_name__startswith=value)
            q_obj |= Q(middle_name__startswith=value)
            q_obj |= Q(family_name__startswith=value)
            q_obj &= inner_query
        return qs.filter(q_obj).distinct()

    def status_filter(self, qs, name, value):
        q_obj = Q()
        if STATUS_DUPLICATE in value:
            q_obj |= Q(duplicate=True)
        if STATUS_WITHDRAWN in value:
            q_obj |= Q(withdrawn=True)
        if STATUS_ACTIVE in value:
            q_obj |= Q(duplicate=False, withdrawn=False)

        return qs.filter(q_obj).distinct()

    def filter_excluded_id(self, qs, name, value):
        return qs.exclude(id=decode_id_string(value))


class DocumentTypeNode(DjangoObjectType):
    country = graphene.String(description="Country name")
    country_iso3 = graphene.String(description="Country ISO3")

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_iso3(parent, info):
        return parent.country.alpha3

    class Meta:
        model = DocumentType


class AgencyNode(DjangoObjectType):
    country = graphene.String(description="Country name")
    country_iso3 = graphene.String(description="Country ISO3")

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_iso3(parent, info):
        return parent.country.alpha3

    class Meta:
        model = Agency


class IndividualIdentityNode(DjangoObjectType):
    type = graphene.String(description="Agency type")
    country = graphene.String(description="Agency country")

    def resolve_type(parent, info):
        return parent.agency.type

    def resolve_country(parent, info):
        return getattr(parent.agency.country, "name", parent.agency.country)

    class Meta:
        model = IndividualIdentity
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class DocumentNode(DjangoObjectType):
    country = graphene.String(description="Document country")
    photo = graphene.String(description="Photo url")

    def resolve_country(parent, info):
        return getattr(parent.type.country, "name", parent.type.country)

    def resolve_photo(parent, info):
        if parent.photo:
            return parent.photo.url
        return

    class Meta:
        model = Document
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


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


class DeliveredQuantityNode(graphene.ObjectType):
    total_delivered_quantity = graphene.Decimal()
    currency = graphene.String()


class ProgramsWithDeliveredQuantityNode(graphene.ObjectType):
    class Meta:
        default_resolver = _custom_dict_or_attr_resolver

    id = graphene.ID()
    name = graphene.String()
    quantity = graphene.List(DeliveredQuantityNode)


class HouseholdNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER),
    )

    admin_area_title = graphene.String(description="Admin area title")
    total_cash_received = graphene.Decimal()
    total_cash_received_usd = graphene.Decimal()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    currency = graphene.String()
    flex_fields = FlexFieldsScalar()
    selection = graphene.Field(HouseholdSelection)
    sanction_list_possible_match = graphene.Boolean()
    sanction_list_confirmed_match = graphene.Boolean()
    has_duplicates = graphene.Boolean(description="Mark household if any of individuals has Duplicate status")
    consent_sharing = graphene.List(graphene.String)
    admin1 = graphene.Field(AdminAreaNode)
    admin2 = graphene.Field(AdminAreaNode)
    status = graphene.String()
    programs_with_delivered_quantity = graphene.List(ProgramsWithDeliveredQuantityNode)

    def resolve_admin_area_title(parent, info):
        if parent.admin_area:
            return parent.admin_area.title
        return ""

    def resolve_programs_with_delivered_quantity(parent, info):
        return parent.programs_with_delivered_quantity

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

    def resolve_flex_fields(parent, info):
        return resolve_flex_fields_choices_to_string(parent)

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
    status = graphene.String()
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
    photo = graphene.String()
    age = graphene.Int()

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

    def resolve_photo(parent, info):
        if parent.photo:
            return parent.photo.url
        return

    def resolve_flex_fields(parent, info):
        return resolve_flex_fields_choices_to_string(parent)

    @staticmethod
    def resolve_age(parent, info):
        return parent.age

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
        convert_choices_to_enum = get_model_choices_fields(
            Individual,
            excluded=[
                "seeing_disability",
                "hearing_disability",
                "physical_disability",
                "memory_disability",
                "selfcare_disability",
                "comms_disability",
                "work_status",
                "collect_individual_data",
            ],
        )


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        filterset_class=HouseholdFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST, *ALL_GRIEVANCES_CREATE_MODIFY),
        ),
    )
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoPermissionFilterConnectionField(
        IndividualNode,
        filterset_class=IndividualFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.POPULATION_VIEW_INDIVIDUALS_LIST, *ALL_GRIEVANCES_CREATE_MODIFY),
        ),
    )

    section_households_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_individuals_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_child_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )

    residence_status_choices = graphene.List(ChoiceObject)
    sex_choices = graphene.List(ChoiceObject)
    marital_status_choices = graphene.List(ChoiceObject)
    work_status_choices = graphene.List(ChoiceObject)
    relationship_choices = graphene.List(ChoiceObject)
    role_choices = graphene.List(ChoiceObject)
    document_type_choices = graphene.List(ChoiceObject)
    identity_type_choices = graphene.List(ChoiceObject)
    countries_choices = graphene.List(ChoiceObject)
    observed_disability_choices = graphene.List(ChoiceObject)
    severity_of_disability_choices = graphene.List(ChoiceObject)
    flag_choices = graphene.List(ChoiceObject)

    all_households_flex_fields_attributes = graphene.List(FieldAttributeNode)
    all_individuals_flex_fields_attributes = graphene.List(FieldAttributeNode)

    def resolve_all_households_flex_fields_attributes(self, info, **kwargs):
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
        ).order_by("created_at")

    def resolve_all_individuals_flex_fields_attributes(self, info, **kwargs):
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
        ).order_by("created_at")

    def resolve_all_households(self, info, **kwargs):
        return Household.objects.annotate(total_cash=Coalesce(Sum("payment_records__delivered_quantity"), 0)).order_by(
            "created_at"
        )

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

    def resolve_identity_type_choices(self, info, **kwargs):
        return to_choice_object(AGENCY_TYPE_CHOICES)

    def resolve_countries_choices(self, info, **kwargs):
        return to_choice_object([(alpha3, label) for (label, alpha2, alpha3) in Countries.get_countries()])

    def resolve_severity_of_disability_choices(self, info, **kwargs):
        return to_choice_object(SEVERITY_OF_DISABILITY_CHOICES)

    def resolve_observed_disability_choices(self, info, **kwargs):
        return to_choice_object(OBSERVED_DISABILITY_CHOICE)

    def resolve_flag_choices(self, info, **kwargs):
        return to_choice_object(INDIVIDUAL_FLAGS_CHOICES)

    def resolve_work_status_choices(self, info, **kwargs):
        return to_choice_object(WORK_STATUS_CHOICE)

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_section_households_reached(self, info, business_area_slug, year, **kwargs):
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        return {"total": payment_records_qs.values_list("household", flat=True).distinct().count()}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_section_individuals_reached(self, info, business_area_slug, year, **kwargs):
        households_individuals_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        individuals_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_individuals_params)
            .distinct("household__id")
        )
        return {"total": sum(sum_lists_with_values(individuals_counts, len(households_individuals_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_section_child_reached(self, info, business_area_slug, year, **kwargs):
        households_child_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
        ]
        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        household_child_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_child_params)
            .distinct("household__id")
        )
        return {"total": sum(sum_lists_with_values(household_child_counts, len(households_child_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_individuals_reached_by_age_and_gender(self, info, business_area_slug, year, **kwargs):
        households_params = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]

        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        household_child_counts = (
            payment_records_qs.select_related("household").values_list(*households_params).distinct("household__id")
        )
        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_individuals_with_disability_reached_by_age(self, info, business_area_slug, year, **kwargs):
        households_params_with_disability = [
            "household__female_age_group_0_5_disabled_count",
            "household__female_age_group_6_11_disabled_count",
            "household__female_age_group_12_17_disabled_count",
            "household__female_age_group_18_59_disabled_count",
            "household__female_age_group_60_disabled_count",
            "household__male_age_group_0_5_disabled_count",
            "household__male_age_group_6_11_disabled_count",
            "household__male_age_group_12_17_disabled_count",
            "household__male_age_group_18_59_disabled_count",
            "household__male_age_group_60_disabled_count",
        ]
        households_params_total = [
            "household__female_age_group_0_5_count",
            "household__female_age_group_6_11_count",
            "household__female_age_group_12_17_count",
            "household__female_age_group_18_59_count",
            "household__female_age_group_60_count",
            "household__male_age_group_0_5_count",
            "household__male_age_group_6_11_count",
            "household__male_age_group_12_17_count",
            "household__male_age_group_18_59_count",
            "household__male_age_group_60_count",
        ]

        payment_records_qs = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        # aggregate with distinct by household__id is not possible
        households_with_disability_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_params_with_disability)
            .distinct("household__id")
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = (
            payment_records_qs.select_related("household")
            .values_list(*households_params_total)
            .distinct("household__id")
        )
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}
