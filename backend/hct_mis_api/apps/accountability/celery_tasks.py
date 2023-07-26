import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.loader import render_to_string

from sentry_sdk import configure_scope

from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def export_survey_sample_task(survey_id: str, user_id: str) -> None:
    try:
        survey = Survey.objects.get(id=survey_id)
        user = get_user_model().objects.get(pk=user_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", survey.business_area)

            service = ExportSurveySampleService(survey, user)
            service.export_sample()

            context = service.get_email_context()
            user.email_user(
                context["title"],
                render_to_string(service.text_template, context=context),
                settings.EMAIL_HOST_USER,
                html_message=render_to_string(service.html_template, context=context),
            )
    except Exception as e:
        logger.exception(e)
        raise


@app.task
@log_start_and_end
@sentry_tags
def send_survey_to_users(survey_id: str) -> None:
    survey = Survey.objects.get(id=survey_id)
    if survey.category == Survey.CATEGORY_MANUAL:
        return
    phone_numbers = survey.recipients.filter(
        Q(head_of_household__phone_no__isnull=False) | ~Q(head_of_household__phone_no="")
    ).values_list("head_of_household__phone_no", flat=True)
    if survey.category == Survey.CATEGORY_SMS:
        api = RapidProAPI(survey.business_area.slug, RapidProAPI.MODE_MESSAGE)
        api.broadcast_message(phone_numbers, survey.body)
        return
    business_area = BusinessArea.objects.get(id=survey.business_area_id)
    api = RapidProAPI(business_area.slug, RapidProAPI.MODE_VERIFICATION)

    already_received = [
        phone_number
        for successful_call in survey.successful_rapid_pro_calls
        for phone_number in successful_call["urns"]
    ]
    phone_numbers = [phone_number for phone_number in phone_numbers if phone_number not in already_received]

    successful_flows, error = api.start_flow(survey.flow_id, phone_numbers)

    for successful_flow in successful_flows:
        survey.successful_rapid_pro_calls.append(
            {
                "flow_uuid": successful_flow.response["uuid"],
                "urns": list(map(str, successful_flow.urns)),
            }
        )
    survey.save()
