import logging
from collections import OrderedDict
from enum import Enum, auto, unique
from functools import partial
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, Union

from django.core.exceptions import PermissionDenied
from django.db.models import Model

from graphene import Mutation
from graphene.relay import ClientIDMutation
from graphene.types.argument import to_arguments
from graphene_django.filter.utils import (
    get_filtering_args_from_filterset,
    get_filterset_class,
)

from hct_mis_api.apps.core.extended_connection import DjangoFastConnectionField
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


@unique
class Permissions(Enum):
    def _generate_next_value_(name: str, start: int, count: int, last_values: List[Any]) -> Any:  # type: ignore # https://github.com/python/mypy/issues/7591
        return name

    # RDI
    RDI_VIEW_LIST = auto()
    RDI_VIEW_DETAILS = auto()
    RDI_IMPORT_DATA = auto()
    RDI_RERUN_DEDUPE = auto()
    RDI_MERGE_IMPORT = auto()
    RDI_REFUSE_IMPORT = auto()

    # Population
    POPULATION_VIEW_HOUSEHOLDS_LIST = auto()
    POPULATION_VIEW_HOUSEHOLDS_DETAILS = auto()
    POPULATION_VIEW_INDIVIDUALS_LIST = auto()
    POPULATION_VIEW_INDIVIDUALS_DETAILS = auto()

    # Programme
    PRORGRAMME_VIEW_LIST_AND_DETAILS = auto()
    PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS = auto()
    PROGRAMME_CREATE = auto()
    PROGRAMME_UPDATE = auto()
    PROGRAMME_REMOVE = auto()
    PROGRAMME_ACTIVATE = auto()
    PROGRAMME_FINISH = auto()

    # Targeting
    TARGETING_VIEW_LIST = auto()
    TARGETING_VIEW_DETAILS = auto()
    TARGETING_CREATE = auto()
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
    PAYMENT_VERIFICATION_DELETE = auto()
    PAYMENT_VERIFICATION_INVALID = auto()
    PAYMENT_VERIFICATION_MARK_AS_FAILED = auto()

    # Payment Module
    PM_VIEW_LIST = auto()
    PM_CREATE = auto()
    PM_VIEW_DETAILS = auto()
    PM_IMPORT_XLSX_WITH_ENTITLEMENTS = auto()
    PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS = auto()

    PM_LOCK_AND_UNLOCK = auto()
    PM_LOCK_AND_UNLOCK_FSP = auto()
    PM_SEND_FOR_APPROVAL = auto()
    PM_ACCEPTANCE_PROCESS_APPROVE = auto()
    PM_ACCEPTANCE_PROCESS_AUTHORIZE = auto()
    PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW = auto()
    PM_IMPORT_XLSX_WITH_RECONCILIATION = auto()

    # Payment Module Admin
    PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE = auto()

    # User Management
    USER_MANAGEMENT_VIEW_LIST = auto()

    # Dashboard
    # Note: view HQ dashboard will be available for users in business area global and permission view_country
    # DASHBOARD_VIEW_HQ = auto()
    DASHBOARD_VIEW_COUNTRY = auto()
    DASHBOARD_EXPORT = auto()

    # Grievances
    # We have different permissions that allow to view/edit etc all grievances
    # or only the ones user created or the ones user is assigned to
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE = auto()
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER = auto()
    GRIEVANCES_CREATE = auto()
    GRIEVANCES_UPDATE = auto()
    GRIEVANCES_UPDATE_AS_CREATOR = auto()
    GRIEVANCES_UPDATE_AS_OWNER = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER = auto()
    GRIEVANCES_ADD_NOTE = auto()
    GRIEVANCES_ADD_NOTE_AS_CREATOR = auto()
    GRIEVANCES_ADD_NOTE_AS_OWNER = auto()
    GRIEVANCES_SET_IN_PROGRESS = auto()
    GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR = auto()
    GRIEVANCES_SET_IN_PROGRESS_AS_OWNER = auto()
    GRIEVANCES_SET_ON_HOLD = auto()
    GRIEVANCES_SET_ON_HOLD_AS_CREATOR = auto()
    GRIEVANCES_SET_ON_HOLD_AS_OWNER = auto()
    GRIEVANCES_SEND_FOR_APPROVAL = auto()
    GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR = auto()
    GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER = auto()
    GRIEVANCES_SEND_BACK = auto()
    GRIEVANCES_SEND_BACK_AS_CREATOR = auto()
    GRIEVANCES_SEND_BACK_AS_OWNER = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER = auto()
    GRIEVANCE_ASSIGN = auto()

    # Reporting
    REPORTING_EXPORT = auto()

    # All
    ALL_VIEW_PII_DATA_ON_LISTS = auto()

    # Activity Log
    ACTIVITY_LOG_VIEW = auto()
    ACTIVITY_LOG_DOWNLOAD = auto()

    # Core
    UPLOAD_STORAGE_FILE = auto()
    DOWNLOAD_STORAGE_FILE = auto()

    # Django Admin
    # ...

    # ...

    @classmethod
    def choices(cls) -> Tuple:
        return tuple((i.value, i.value.replace("_", " ")) for i in cls)


ALL_GRIEVANCES_CREATE_MODIFY = (
    Permissions.GRIEVANCES_CREATE,
    Permissions.GRIEVANCES_UPDATE,
    Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
    Permissions.GRIEVANCES_UPDATE_AS_OWNER,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
)


class BasePermission:
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return False


class AllowAny(BasePermission):
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return True


class AllowAuthenticated(BasePermission):
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return info.context.user.is_authenticated


def check_permissions(user: Any, permissions: Iterable[Permissions], **kwargs: Any) -> bool:
    if not user.is_authenticated:
        return False
    business_area_arg = kwargs.get("business_area")
    if business_area_arg is None:
        return False
    if isinstance(business_area_arg, BusinessArea):
        business_area = business_area_arg
    else:
        business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
    if business_area is None:
        return False
    return any(user.has_permission(permission.name, business_area) for permission in permissions)


def hopePermissionClass(permission: Permissions) -> Type[BasePermission]:
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info: Any, **kwargs: Any) -> bool:
            user = info.context.user
            permissions = [permission]
            return check_permissions(user, permissions, **kwargs)

    return XDPerm


def hopeOneOfPermissionClass(*permissions: Permissions) -> Type[BasePermission]:
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info: Any, **kwargs: Any) -> bool:
            user = info.context.user
            return check_permissions(user, permissions, **kwargs)

    return XDPerm


class BaseNodePermissionMixin:
    permission_classes: Tuple[Type[BasePermission], ...] = (AllowAny,)

    @classmethod
    def check_node_permission(cls, info: Any, object_instance: Any) -> None:
        business_area = object_instance.business_area
        if not any(perm.has_permission(info, business_area=business_area) for perm in cls.permission_classes):
            raise PermissionDenied("Permission Denied")

    @classmethod
    def get_node(cls, info: Any, object_id: str) -> Optional[Model]:
        try:
            object_instance = cls._meta.model.objects.get(pk=object_id)
            cls.check_node_permission(info, object_instance)
        except cls._meta.model.DoesNotExist:
            object_instance = None
        return object_instance

    @classmethod
    def check_creator_or_owner_permission(
        cls,
        info: Any,
        object_instance: Any,
        general_permission: str,
        is_creator: bool,
        creator_permission: str,
        is_owner: bool,
        owner_permission: str,
    ) -> None:
        user = info.context.user
        business_area = object_instance.business_area
        if not user.is_authenticated or not (
            user.has_permission(general_permission, business_area)
            or (is_creator and user.has_permission(creator_permission, business_area))
            or (is_owner and user.has_permission(owner_permission, business_area))
        ):
            raise PermissionDenied("Permission Denied")


class DjangoPermissionFilterFastConnectionField(DjangoFastConnectionField):
    def __init__(
        self,
        type: Type,
        fields: Optional[Any] = None,
        order_by: Optional[Any] = None,
        extra_filter_meta: Optional[Any] = None,
        filterset_class: Optional[Any] = None,
        permission_classes: Tuple[Type[BasePermission], ...] = (AllowAny,),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        self.permission_classes = permission_classes
        super().__init__(type, *args, **kwargs)

    @property
    def args(self) -> Dict:
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args: Any) -> None:
        self._base_args = args

    @property
    def filterset_class(self) -> Any:
        if not self._filterset_class:
            fields = self._fields or self.node_type._meta.filter_fields
            meta = dict(model=self.model, fields=fields)
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (self.node_type._meta.filterset_class)
            self._filterset_class = get_filterset_class(filterset_class, **meta)

        return self._filterset_class

    @property
    def filtering_args(self) -> Any:
        return get_filtering_args_from_filterset(self.filterset_class, self.node_type)

    @classmethod
    def resolve_queryset(
        cls,
        connection: Any,
        iterable: Iterable,
        info: Any,
        args: Any,
        filtering_args: List,
        filterset_class: Any,
        permission_classes: List,
    ) -> Any:
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        if not any(perm.has_permission(info, **filter_kwargs) for perm in permission_classes):
            raise PermissionDenied("Permission Denied")
        if "permissions" in filtering_args:
            filter_kwargs["permissions"] = info.context.user.permissions_in_business_area(
                filter_kwargs.get("business_area")
            )
        qs = super().resolve_queryset(connection, iterable, info, args)
        return filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

    def get_queryset_resolver(self) -> Callable:
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            permission_classes=self.permission_classes,
        )


class DjangoPermissionFilterConnectionField(DjangoPermissionFilterFastConnectionField):
    use_cached_count = False


class BaseMutationPermissionMixin:
    @classmethod
    def is_authenticated(cls, info: Any) -> Optional[bool]:
        if not info.context.user.is_authenticated:
            cls.raise_not_authenticated_error()
        return True

    @classmethod
    def has_permission(
        cls, info: Any, permission: Any, business_area_arg: Union[str, BusinessArea], raise_error: bool = True
    ) -> bool:
        cls.is_authenticated(info)
        permissions: Iterable = (permission,) if not isinstance(permission, list) else permission
        if isinstance(business_area_arg, BusinessArea):
            business_area = business_area_arg
        else:
            if business_area_arg is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
            business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
            if business_area is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
        if not any(
            [
                permission.name
                for permission in permissions
                if info.context.user.has_permission(permission.name, business_area)
            ]
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @classmethod
    def has_creator_or_owner_permission(
        cls,
        info: Any,
        business_area_arg: str,
        general_permission: Any,
        is_creator: bool,
        creator_permission: Any,
        is_owner: bool,
        owner_permission: Any,
        raise_error: bool = True,
    ) -> bool:
        cls.is_authenticated(info)
        if not (
            cls.has_permission(info, general_permission, business_area_arg, False)
            or (is_creator and cls.has_permission(info, creator_permission, business_area_arg, False))
            or (is_owner and cls.has_permission(info, owner_permission, business_area_arg, False))
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @staticmethod
    def raise_permission_denied_error(raise_error: bool = True) -> bool:
        if not raise_error:
            return False
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    @staticmethod
    def raise_not_authenticated_error() -> None:
        raise PermissionDenied("Permission Denied: User is not authenticated.")


class PermissionMutation(BaseMutationPermissionMixin, Mutation):
    @classmethod
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> None:
        return super().mutate(root, info, **kwargs)


class PermissionRelayMutation(BaseMutationPermissionMixin, ClientIDMutation):
    @classmethod
    def mutate_and_get_payload(cls, root: Any, info: Any, **kwargs: Any) -> None:
        return super().mutate_and_get_payload(root, info, **kwargs)
