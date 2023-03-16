import logging
from typing import Any, Union

from hct_mis_api.apps.utils.sentry import sentry_tags

from ..core.celery import app
from .models import Query, Report
from .utils import should_run

logger = logging.getLogger(__name__)


@app.task()
@sentry_tags
def spawn(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def complete(query_id: int, **kwargs: Any) -> None:
    query = Query.objects.get(pk=query_id)
    query.run(True, kwargs)


@app.task()
@sentry_tags
def run_background_query(query_id: int, **kwargs: Any) -> Union[str, bool, None]:
    try:
        query = Query.objects.get(pk=query_id)
        query.execute_matrix()
    except BaseException as e:
        logger.exception(e)
        return False
    return "Ok"


@app.task()
@sentry_tags
def refresh_reports() -> None:
    try:
<<<<<<< HEAD
        for report in Report.objects.filter(active=True, refresh_daily=True):
            run_background_query.delay(report.query.id)
            with atomic():
                report.last_run = timezone.now()
                report.execute()
    except Exception as e:
=======
        for report in Report.objects.filter(active=True, frequence__isnull=False):
            if should_run(report.frequence):
                report.execute(run_query=True)
    except BaseException as e:
>>>>>>> origin
        logger.exception(e)
