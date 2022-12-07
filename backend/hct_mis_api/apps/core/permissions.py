import logging
from typing import Any, Callable

from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def is_authenticated(func: Callable) -> Any:
    """
    Simple decorator for use with Graphene mutate method
    to check if user is authenticated.
    """

    def wrapper(cls: Any, root: Any, info: Any, *args: Any, **kwargs: Any) -> Any:
        if not info.context.user.is_authenticated:
            logger.error(f"Permission Denied for {info.context.user}, User is not authenticated.")
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return func(cls, root, info, *args, **kwargs)

    return wrapper
