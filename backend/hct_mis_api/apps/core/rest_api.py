import logging

from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers


from hct_mis_api.apps.core.models import FlexibleAttribute, FlexibleAttributeChoice
from hct_mis_api.apps.core.schema import sort_by_attr, get_fields_attr_generators
from hct_mis_api.apps.core.utils import LazyEvalMethodsDict


logger = logging.getLogger(__name__)


def attr_resolver(attname, default_value, obj):
    return getattr(obj, attname, default_value)


def dict_resolver(attname, default_value, obj):
    return obj.get(attname, default_value)


def _custom_dict_or_attr_resolver(attname, default_value, obj):
    resolver = attr_resolver
    if isinstance(obj, (dict, LazyEvalMethodsDict)):
        resolver = dict_resolver
    return resolver(attname, default_value, obj)


def resolve_label(obj):
    return [{"language": k, "label": v} for k, v in obj.items()]


class LabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    language = serializers.CharField()


class CoreFieldChoiceSerializer(serializers.Serializer):
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    admin = serializers.CharField(default=None)
    list_name = serializers.CharField(default=None)

    def get_labels(self, obj):
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_value(self, obj):
        if isinstance(obj, FlexibleAttributeChoice):
            return obj.name
        return _custom_dict_or_attr_resolver("value", None, obj)

    def get_label_en(self, obj):
        return _custom_dict_or_attr_resolver("label", None, obj)["English(EN)"]


class FieldAttributeSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    name = serializers.CharField()
    labels = serializers.SerializerMethodField()
    label_en = serializers.SerializerMethodField()
    hint = serializers.CharField()
    choices = CoreFieldChoiceSerializer(many=True)
    associated_with = serializers.SerializerMethodField()
    is_flex_field = serializers.SerializerMethodField()

    def get_labels(self, obj):
        return resolve_label(_custom_dict_or_attr_resolver("label", None, obj))

    def get_label_en(self, obj):
        return _custom_dict_or_attr_resolver("label", None, obj)["English(EN)"]

    def get_is_flex_field(self, obj):
        if isinstance(obj, FlexibleAttribute):
            return True
        return False

    def get_associated_with(self, obj):
        resolved = _custom_dict_or_attr_resolver("associated_with", None, obj)
        if resolved == 0:
            return "Household"
        elif resolved == 1:
            return "Individual"
        else:
            return resolved


@api_view()
def all_fields_attributes(request):
    flex_field = request.data.get("flex_field", True)
    business_area_slug = request.data.get("business_area_slug")

    records = cache.get(business_area_slug)
    if records:
        return Response(records)

    records = sort_by_attr(get_fields_attr_generators(flex_field, business_area_slug), "label.English(EN)")
    serializer = FieldAttributeSerializer(records, many=True)
    data = serializer.data

    cache.set(business_area_slug, data)

    return Response(data)
