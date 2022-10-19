import sys
from types import FunctionType
from typing import Any

from sentry_sdk import configure_scope


class SentryScopeMiddleware:
    def __init__(self, get_response: FunctionType) -> None:
        self.get_response = get_response
        super().__init__()

    # Note: must be listed AFTER AuthenticationMiddleware
    def __call__(self, request: Any) -> Any:
        sys.stderr.isatty = lambda: False
        with configure_scope() as scope:
            scope.set_tag("username", request.user.username)
            scope.set_tag("business_area", request.headers.get("Business-Area"))
            response = self.get_response(request)
        return response
