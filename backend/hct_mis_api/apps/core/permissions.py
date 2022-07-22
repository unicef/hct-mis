import logging

from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)


def is_authenticated(func):
    """
    Simple decorator for use with Graphene mutate method
    to check if user is authenticated.
    """

    def wrapper(cls, root, info, *args, **kwargs):
        if not info.context.user.is_authenticated:
            logger.error(
                f"Permission Denied for user={info.context.user.email}, User is not authenticated."
            )
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return func(cls, root, info, *args, **kwargs)

    return wrapper
