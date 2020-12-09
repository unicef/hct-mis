from functools import partial
from enum import unique, auto, Enum

from django.core.exceptions import PermissionDenied
from graphene import Mutation
from graphene.types.argument import to_arguments
from graphene_django import DjangoConnectionField
from graphene_django.filter.utils import get_filtering_args_from_filterset, get_filterset_class
from graphql import GraphQLError
from collections import OrderedDict

from core.models import BusinessArea


@unique
class Permissions(Enum):
    def _generate_next_value_(name, *args):
        return name

    # RDI
    RDI_VIEW_LIST = auto()
    RDI_VIEW_DETAILS = auto()
    RDI_IMPORT_DATA = auto()
    RDI_RERUN_DEDUPE = auto()
    RDI_MERGE_IMPORT = auto()

    # Population
    POPULATION_VIEW_HOUSEHOLDS_LIST = auto()
    POPULATION_VIEW_HOUSEHOLDS_DETAILS = auto()
    POPULATION_VIEW_INDIVIDUALS_LIST = auto()
    POPULATION_VIEW_INDIVIDUALS_DETAILS = auto()

    # Programme
    PRORGRAMME_VIEW_LIST_AND_DETAILS = auto()
    PROGRAMME_CREATE = auto()
    PROGRAMME_UPDATE = auto()
    PROGRAMME_REMOVE = auto()
    PROGRAMME_ACTIVATE = auto()
    PROGRAMME_FINISH = auto()

    # Targeting
    TARGETING_VIEW_LIST = auto()
    TARGETING_VIEW_DETAILS = auto()
    TARGETING_UPDATE = auto()
    TARGETING_DUPLICATE = auto()
    TARGETING_REMOVE = auto()
    TARGETING_LOCK = auto()
    TARGETING_UNLOCK = auto()
    TARGETING_SEND = auto()

    # Payment Verification
    PAYMENT_VERIFICATION_VIEW_LIST = auto()
    PAYMENT_VERIFICATION_VIEW_DETAILS = auto()
    PAYMENT_VERIFICATION_CREATE = auto()
    PAYMENT_VERIFICATION_UPDATE = auto()
    PAYMENT_VERIFICATION_ACTIVATE = auto()
    PAYMENT_VERIFICATION_DISCARD = auto()
    PAYMENT_VERIFICATION_FINISH = auto()
    PAYMENT_VERIFICATION_EXPORT = auto()
    PAYMENT_VERIFICATION_IMPORT = auto()
    PAYMENT_VERIFICATION_VERIFY = auto()
    PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS = auto()

    # User Management
    USER_MANAGEMENT_VIEW_LIST = auto()

    # Dashboard
    DASHBOARD_VIEW_HQ = auto()
    DASHBOARD_VIEW_COUNTRY = auto()
    DASHBOARD_EXPORT = auto()

    # Grievances
    # ...

    # Django Admin
    # ...

    # ...

    @classmethod
    def choices(cls):
        return tuple((i.value, i.value.replace("_", " ")) for i in cls)


class BasePermission:
    @classmethod
    def has_permission(cls, info, **kwargs):
        return False


class AllowAny(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return True


class AllowAuthenticated(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return info.context.user.is_authenticated


def hopePermissionClass(permission):
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info, **kwargs):
            business_area_arg = kwargs.get("business_area")
            if isinstance(business_area_arg, BusinessArea):
                business_area = business_area_arg
            else:
                if business_area_arg is None:
                    return False
                business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
                if business_area is None:
                    return False
            return info.context.user.has_permission(permission.name, business_area)

    return XDPerm


class BaseNodePermissionMixin:
    permission_classes = (AllowAny,)

    @classmethod
    def check_node_permission(cls, info, object_instance):
        business_area = object_instance.business_area
        if not all((perm.has_permission(info, business_area=business_area) for perm in cls.permission_classes)):
            raise GraphQLError("Permission Denied")

    @classmethod
    def get_node(cls, info, id):
        try:
            object_instance = cls._meta.model.objects.get(pk=id)  # type: ignore
            cls.check_node_permission(info, object_instance)
        except cls._meta.model.DoesNotExist:  # type: ignore
            object_instance = None
        return object_instance


class DjangoPermissionFilterConnectionField(DjangoConnectionField):
    def __init__(
        self,
        type,
        fields=None,
        order_by=None,
        extra_filter_meta=None,
        filterset_class=None,
        permission_classes=(AllowAny,),
        *args,
        **kwargs,
    ):
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        self.permission_classes = permission_classes
        super(DjangoPermissionFilterConnectionField, self).__init__(type, *args, **kwargs)

    @property
    def args(self):
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args):
        self._base_args = args

    @property
    def filterset_class(self):
        if not self._filterset_class:
            fields = self._fields or self.node_type._meta.filter_fields
            meta = dict(model=self.model, fields=fields)
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (self.node_type._meta.filterset_class)
            self._filterset_class = get_filterset_class(filterset_class, **meta)

        return self._filterset_class

    @property
    def filtering_args(self):
        return get_filtering_args_from_filterset(self.filterset_class, self.node_type)

    @classmethod
    def resolve_queryset(cls, connection, iterable, info, args, filtering_args, filterset_class, permission_classes):
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        if not all((perm.has_permission(info, **filter_kwargs) for perm in permission_classes)):
            raise GraphQLError("Permission Denied")
        qs = super(DjangoPermissionFilterConnectionField, cls).resolve_queryset(connection, iterable, info, args)
        return filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

    def get_queryset_resolver(self):
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            permission_classes=self.permission_classes,
        )


class PermissionMutationMixin(Mutation):
    @classmethod
    def is_authenticated(cls, info):
        if not info.context.user.is_authenticated:
            cls.raise_permission_denied_error(True)
        return True

    @classmethod
    def has_permission(cls, info, permission, business_area_arg):
        cls.is_authenticated(info)
        if not isinstance(permission, list):
            permissions = (permission,)
        else:
            permissions = permission
        if isinstance(business_area_arg, BusinessArea):
            business_area = business_area_arg
        else:
            if business_area_arg is None:
                cls.raise_permission_denied_error()
            business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
            if business_area is None:
                cls.raise_permission_denied_error()
        if not any(
            [
                permission.name
                for permission in permissions
                if info.context.user.has_permission(permission.name, business_area)
            ]
        ):
            cls.raise_permission_denied_error()
        return True

    @staticmethod
    def raise_permission_denied_error(not_authenticated=False):
        if not_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        else:
            raise PermissionDenied("Permission Denied: User does not have correct permission.")

    @classmethod
    def mutate(cls, root, info, **kwargs):
        return super().mutate(root, info, **kwargs)
