from django.utils.functional import cached_property

from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from ..auth import HOPEAuthentication, HOPEPermission
from ..models import APILogEntry


class SelectedBusinessAreaMixin:
    @cached_property
    def selected_business_area(self):
        return self.request.auth.valid_for.all().get(slug=self.kwargs.get("business_area", None))
        # return BusinessArea.objects.filter(slug__in=self.request.auth.valid_for.all()).get(
        #     slug=self.kwargs.get("business_area", None)
        # )


class HOPEAPIView(APIView):
    permission_classes = [HOPEPermission]
    authentication_classes = [HOPEAuthentication]
    permission = "any"
    log_http_methods = ["POST", "PUT", "DELETE"]

    def dispatch(self, request, *args, **kwargs):
        ret = super().dispatch(request, *args, **kwargs)
        if request.method.upper() in self.log_http_methods and (ret.status_code < 300 or ret.status_code > 400):
            log = APILogEntry.objects.create(
                token=request.auth,
                url=request.path,
                method=request.method.upper(),
                status_code=ret.status_code,
            )
            assert log.pk

        return ret

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            exc = PermissionDenied(f"{exc.detail} {self.permission}")

        return super().handle_exception(exc)


class HOPEAPIBusinessAreaView(SelectedBusinessAreaMixin, HOPEAPIView):
    permission_classes = [HOPEPermission]
    authentication_classes = [HOPEAuthentication]
    permission = "any"
