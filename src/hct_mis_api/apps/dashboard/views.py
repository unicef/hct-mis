import json
import logging
from typing import Any

from django.core.cache import cache

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import generate_dash_report_task
from hct_mis_api.apps.dashboard.models import DashReport
from hct_mis_api.apps.utils.sentry import sentry_tags

log = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 6  # 6 hours


class DashboardReportdView(APIView):
    """
    API View to retrieve a DashReport for a specific business area.
    Only authenticated users can access this view.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def get(self, request: Any, business_area_slug: str) -> Response:
        """
        Retrieve the DashReport for a given business area.

        Args:
            request: The HTTP request object.
            business_area_slug (str): The slug of the business area.

        Returns:
            Response: JSON response containing the report data or an error message.
        """
        cache_key = f"dashboard_report_{business_area_slug}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        try:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            dash_report = DashReport.objects.get(business_area=business_area)

            if dash_report.status != DashReport.COMPLETED or not dash_report.file:
                return Response(
                    {"detail": "Report is either not completed or does not have a file."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with open(dash_report.file.path, "r") as file:
                file_contents = json.load(file)
            cache.set(cache_key, file_contents, CACHE_TIMEOUT)
            return Response(file_contents, status=status.HTTP_200_OK)

        except BusinessArea.DoesNotExist:
            log.error(f"Business area with slug {business_area_slug} not found.")
            return Response({"detail": "Business area not found."}, status=status.HTTP_404_NOT_FOUND)
        except DashReport.DoesNotExist:
            log.error(f"Report not found for business area with slug {business_area_slug}.")
            return Response({"detail": "Report not found for this business area."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log.exception(f"An error occurred while fetching the report for {business_area_slug}: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateOrUpdateDashReportView(APIView):
    """
    API to trigger the creation or update of a DashReport for a given business area.
    Restricted to superusers.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def post(self, request: Any, business_area_slug: str) -> Response:
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers are allowed to create or update DashReports.")

        try:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            generate_dash_report_task.delay(business_area.slug)
            cache_key = f"dashboard_report_{business_area_slug}"
            cache.delete(cache_key)

            return Response(
                {"detail": "DashReport generation task has been triggered."}, status=status.HTTP_202_ACCEPTED
            )

        except BusinessArea.DoesNotExist:
            return Response({"detail": "Business area not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
