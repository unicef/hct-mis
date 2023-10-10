from typing import TYPE_CHECKING, Any, Optional

from django.utils.translation import gettext_lazy as _

from django_countries import Countries
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    SEX_CHOICE,
)
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from rest_framework.request import Request


COLLECT_TYPE_UNKNOWN = ""
COLLECT_TYPE_NONE = "0"
COLLECT_TYPE_FULL = "1"
COLLECT_TYPE_PARTIAL = "2"

COLLECT_TYPES = (
    (COLLECT_TYPE_UNKNOWN, _("Unknown")),
    (COLLECT_TYPE_PARTIAL, _("Partial individuals collected")),
    (COLLECT_TYPE_FULL, _("Full individual collected")),
    (COLLECT_TYPE_NONE, _("No individual data")),
)


class DocumentType(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(IDENTIFICATION_TYPE_CHOICE))


class Country(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(Countries()))


class ResidenceStatus(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(RESIDENCE_STATUS_CHOICE))


class MaritalStatus(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(MARITAL_STATUS_CHOICE))


class ObservedDisability(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(OBSERVED_DISABILITY_CHOICE))


class Relationship(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(RELATIONSHIP_CHOICE))


class Roles(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(ROLE_CHOICE))


class Sex(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(SEX_CHOICE))


class Sector(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(Program.SECTOR_CHOICE))


class FrequencyOfPayments(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(Program.FREQUENCY_OF_PAYMENTS_CHOICE))


class ProgramScope(HOPEAPIView):
    def get(self, request: "Request", format: Optional[Any] = None) -> Response:
        return Response(dict(Program.SCOPE_CHOICE))
