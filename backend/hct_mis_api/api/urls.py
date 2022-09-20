from django.urls import include, path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import endpoints
from .router import APIRouter

app_name = "api"

schema_view = get_schema_view(
    openapi.Info(
        title="Hope API documentation",
        default_version='v1',
        description="Hope API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

router = APIRouter()

urlpatterns = [
    re_path(r'^doc/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^doc/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^doc/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    re_path(r"", include(router.urls)),
    path("rdi/<slug:business_area>/upload/", endpoints.UploadRDIView().as_view(), name="rdi-upload"),
    path("rdi/<slug:business_area>/create/", endpoints.CreateRDIView().as_view(), name="rdi-create"),
    path("rdi/<slug:business_area>/<slug:rdi>/push/", endpoints.PushToRDIView().as_view(), name="rdi-push"),
    path("areas/", endpoints.AreaList().as_view(), name="area-list"),
    path("areatypes/", endpoints.AreaTypeList().as_view(), name="areatype-list"),
    path("lookups/document/", endpoints.DocumentType().as_view(), name="document-list"),
    path("lookups/country/", endpoints.Country().as_view(), name="country-list"),
    path("lookups/residencestatus/", endpoints.ResidenceStatus().as_view(), name="residencestatus-list"),
    path("lookups/maritalstatus/", endpoints.MaritalStatus().as_view(), name="maritalstatus-list"),
    path("lookups/observeddisability/", endpoints.ObservedDisability().as_view(), name="observeddisability-list"),
    path("lookups/relationship/", endpoints.Relationship().as_view(), name="relationship-list"),
    path("lookups/datacollectingpolicy/", endpoints.DataCollectingPolicy().as_view(), name="datacollectingpolicy-list"),
    path("lookups/role/", endpoints.Roles().as_view(), name="role-list"),
]
