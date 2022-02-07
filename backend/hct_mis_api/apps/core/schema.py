import logging
from collections import Iterable

from django.core.exceptions import ObjectDoesNotExist

import graphene
from constance import config
from django_filters import CharFilter, FilterSet
from graphene import Boolean, Connection, ConnectionField, DateTime, String, relay
from graphene.types.resolver import attr_resolver, dict_or_attr_resolver, dict_resolver
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from hct_mis_api.apps.core.core_fields_attributes import (
    FILTERABLE_CORE_FIELDS_ATTRIBUTES,
    ROLE_FIELD,
    XLSX_ONLY_FIELDS,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import IntegerFilter
from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.kobo.common import reduce_asset, reduce_assets_list
from hct_mis_api.apps.core.models import (
    AdminArea,
    AdminAreaLevel,
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    FlexibleAttributeGroup,
)
from hct_mis_api.apps.core.utils import LazyEvalMethodsDict

logger = logging.getLogger(__name__)


class AdminAreaFilter(FilterSet):
    business_area = CharFilter(
        field_name="admin_area_level__country__business_areas__slug",
    )
    title__istartswith = CharFilter(field_name="title", lookup_expr="istartswith")
    level = IntegerFilter(
        field_name="level",
    )

    class Meta:
        model = AdminArea
        fields = [
            "title",
            "title__istartswith",
            # "business_area": ["exact"],
        ]


class ChoiceObject(graphene.ObjectType):
    name = String()
    value = String()


class AdminAreaNode(DjangoObjectType):
    class Meta:
        model = AdminArea
        exclude_fields = ["geom", "point"]
        filter_fields = ["title"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AdminAreaTypeNode(DjangoObjectType):
    class Meta:
        model = AdminAreaLevel
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class BusinessAreaNode(DjangoObjectType):
    class Meta:
        model = BusinessArea
        filter_fields = ["id", "slug"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FlexibleAttributeChoiceNode(DjangoObjectType):
    name = graphene.String()
    value = graphene.String(source="label")

    class Meta:
        model = FlexibleAttributeChoice
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        exclude_fields = []


class FlexibleAttributeNode(DjangoObjectType):
    choices = graphene.List(FlexibleAttributeChoiceNode)
    associated_with = graphene.String()

    def resolve_choices(self, info):
        return self.choices.all()

    def resolve_associated_with(self, info):
        return str(FlexibleAttribute.ASSOCIATED_WITH_CHOICES[self.associated_with][1])

    class Meta:
        model = FlexibleAttribute
        fields = [
            "id",
            "type",
            "name",
            "label",
            "hint",
            "required",
        ]


class LabelNode(graphene.ObjectType):
    language = graphene.String()
    label = graphene.String()


def resolve_label(parent):
    labels = []
    for k, v in parent.items():
        labels.append({"language": k, "label": v})
    return labels


class CoreFieldChoiceObject(graphene.ObjectType):
    labels = graphene.List(LabelNode)
    label_en = String()
    value = String()
    admin = String()
    list_name = String()

    def resolve_label_en(parent, info):
        return dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    def resolve_value(parent, info):
        if isinstance(parent, FlexibleAttributeChoice):
            return parent.name
        return dict_or_attr_resolver("value", None, parent, info)

    def resolve_labels(parent, info):
        return resolve_label(dict_or_attr_resolver("label", None, parent, info))


def _custom_dict_or_attr_resolver(attname, default_value, root, info, **args):
    resolver = attr_resolver
    if isinstance(root, (dict, LazyEvalMethodsDict)):
        resolver = dict_resolver
    return resolver(attname, default_value, root, info, **args)


def sort_by_attr(options, attrs: str) -> list:
    def key_extractor(el):
        for attr in attrs.split("."):
            el = _custom_dict_or_attr_resolver(attr, None, el, None)
        return el

    return list(sorted(options, key=key_extractor))


class FieldAttributeNode(graphene.ObjectType):
    class Meta:
        default_resolver = _custom_dict_or_attr_resolver

    id = graphene.String()
    type = graphene.String()
    name = graphene.String()
    labels = graphene.List(LabelNode)
    label_en = String()
    hint = graphene.String()
    required = graphene.Boolean()
    choices = graphene.List(CoreFieldChoiceObject)
    associated_with = graphene.String()
    is_flex_field = graphene.Boolean()

    def resolve_choices(parent, info):
        if isinstance(
            _custom_dict_or_attr_resolver("choices", None, parent, info),
            Iterable,
        ):
            return sorted(parent["choices"], key=lambda elem: elem["label"]["English(EN)"])
        return _custom_dict_or_attr_resolver("choices", None, parent, info).order_by("name").all()

    def resolve_is_flex_field(self, info):
        if isinstance(self, FlexibleAttribute):
            return True
        return False

    def resolve_labels(parent, info):
        return resolve_label(_custom_dict_or_attr_resolver("label", None, parent, info))

    def resolve_label_en(parent, info):
        return _custom_dict_or_attr_resolver("label", None, parent, info)["English(EN)"]

    def resolve_associated_with(self, info):
        resolved = _custom_dict_or_attr_resolver("associated_with", None, self, info)
        if resolved == 0:
            return "Household"
        elif resolved == 1:
            return "Individual"
        else:
            return resolved


class GroupAttributeNode(DjangoObjectType):
    label_en = graphene.String()
    flex_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )

    class Meta:
        model = FlexibleAttributeGroup
        fields = ["id", "name", "label", "flex_attributes", "label_en"]

    def resolve_label_en(self, info):
        return _custom_dict_or_attr_resolver("label", None, self, info)["English(EN)"]

    def resolve_flex_attributes(self, info):
        return self.flex_attributes.all()


class KoboAssetObject(graphene.ObjectType):
    id = String()
    name = String()
    sector = String()
    country = String()
    asset_type = String()
    date_modified = DateTime()
    deployment_active = Boolean()
    has_deployment = Boolean()
    xls_link = String()


class KoboAssetObjectConnection(Connection):
    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return len(self.iterable)

    class Meta:
        node = KoboAssetObject


def get_fields_attr_generators(flex_field):
    if flex_field is not False:
        yield from FlexibleAttribute.objects.order_by("created_at")
    if flex_field is not True:
        yield from FILTERABLE_CORE_FIELDS_ATTRIBUTES
        yield from XLSX_ONLY_FIELDS
        yield ROLE_FIELD


def resolve_assets(business_area_slug, uid: str = None, *args, **kwargs):
    if uid is not None:
        method = KoboAPI(business_area_slug).get_single_project_data(uid)
        return_method = reduce_asset
    else:
        method = KoboAPI(business_area_slug).get_all_projects_data()
        return_method = reduce_assets_list
    try:
        assets = method
    except ObjectDoesNotExist:
        logger.exception(f"Provided business area: {business_area_slug}, does not exist.")
        raise GraphQLError("Provided business area does not exist.")
    except AttributeError as error:
        logger.exception(error)
        raise GraphQLError(str(error))

    return return_method(assets, only_deployed=kwargs.get("only_deployed", False))


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AdminAreaNode)
    business_area = graphene.Field(
        BusinessAreaNode,
        business_area_slug=graphene.String(required=True, description="The business area slug"),
        description="Single business area",
    )
    all_admin_areas = DjangoFilterConnectionField(AdminAreaNode, filterset_class=AdminAreaFilter)
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    all_fields_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )
    all_individual_fields_attributes = graphene.List(
        FieldAttributeNode,
        flex_field=graphene.Boolean(),
        description="All field datatype meta.",
    )
    all_groups_with_fields = graphene.List(
        GroupAttributeNode,
        description="Get all groups that contains flex fields",
    )
    kobo_project = graphene.Field(
        KoboAssetObject,
        uid=graphene.String(required=True),
        business_area_slug=graphene.String(required=True),
        description="Single Kobo project/asset.",
    )
    all_kobo_projects = ConnectionField(
        KoboAssetObjectConnection,
        business_area_slug=graphene.String(required=True),
        only_deployed=graphene.Boolean(required=False),
        description="All Kobo projects/assets.",
    )
    cash_assist_url_prefix = graphene.String()

    def resolve_business_area(parent, info, business_area_slug):
        return BusinessArea.objects.get(slug=business_area_slug)

    def resolve_all_business_areas(parent, info):
        return BusinessArea.objects.filter(is_split=False)

    def resolve_cash_assist_url_prefix(parent, info):
        return config.CASH_ASSIST_URL_PREFIX

    def resolve_all_fields_attributes(parent, info, flex_field=None):
        return sort_by_attr(get_fields_attr_generators(flex_field), "label.English(EN)")

    def resolve_all_individual_fields_attributes(parent, info, flex_field=None):
        return sort_by_attr(get_fields_attr_generators(flex_field), "label.English(EN)")

    def resolve_kobo_project(self, info, uid, business_area_slug, **kwargs):
        return resolve_assets(business_area_slug=business_area_slug, uid=uid)

    def resolve_all_kobo_projects(self, info, business_area_slug, *args, **kwargs):
        return resolve_assets(
            business_area_slug=business_area_slug,
            only_deployed=kwargs.get("only_deployed", False),
        )

    def resolve_all_groups_with_fields(self, info, **kwargs):
        return FlexibleAttributeGroup.objects.distinct().filter(flex_attributes__isnull=False)
