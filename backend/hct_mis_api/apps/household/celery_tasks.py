import logging
from typing import List, Optional
from uuid import UUID

from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

from concurrency.api import disable_concurrency
from constance import config
from sentry_sdk import configure_scope

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.models import COLLECT_TYPE_FULL, COLLECT_TYPE_PARTIAL
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task()
@log_start_and_end
@sentry_tags
def recalculate_population_fields_chunk_task(households_ids: List[UUID]) -> None:
    from hct_mis_api.apps.household.models import Household, Individual

    households_to_update = []
    fields_to_update = []

    with configure_scope() as scope:
        with disable_concurrency(Household), disable_concurrency(Individual):
            with transaction.atomic():
                for hh in (
                    Household.objects.filter(pk__in=households_ids)
                    .only("id", "collect_individual_data")
                    .prefetch_related("individuals")
                    .select_for_update(of=("self",))
                ):
                    scope.set_tag("business_area", hh.business_area)
                    household, updated_fields = recalculate_data(hh, save=False)
                    households_to_update.append(household)
                    fields_to_update.extend(x for x in updated_fields if x not in fields_to_update)

                Household.objects.bulk_update(households_to_update, fields_to_update)


@app.task()
@log_start_and_end
@sentry_tags
def recalculate_population_fields_task(household_ids: Optional[List[UUID]] = None) -> None:
    from hct_mis_api.apps.household.models import Household

    params = {}
    if household_ids:
        params["pk__in"] = household_ids

    queryset = (
        Household.objects.filter(**params)
        .only("pk")
        .filter(collect_individual_data__in=(COLLECT_TYPE_FULL, COLLECT_TYPE_PARTIAL))
        .order_by("pk")
    )
    paginator = Paginator(queryset, config.RECALCULATE_POPULATION_FIELDS_CHUNK)

    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        recalculate_population_fields_chunk_task.delay(
            households_ids=list(page.object_list.values_list("pk", flat=True))
        )


@app.task()
@log_start_and_end
@sentry_tags
def interval_recalculate_population_fields_task() -> None:
    from hct_mis_api.apps.household.models import Individual

    datetime_now = timezone.now()
    now_day, now_month = datetime_now.day, datetime_now.month

    households = (
        Individual.objects.filter(birth_date__day=now_day, birth_date__month=now_month)
        .values_list("household_id", flat=True)
        .distinct()
    )

    recalculate_population_fields_task.delay(households_ids=list(households))


@app.task()
@sentry_tags
def calculate_children_fields_for_not_collected_individual_data() -> int:
    from django.db.models.functions import Coalesce

    from hct_mis_api.apps.household.models import (
        COLLECT_TYPE_FULL,
        COLLECT_TYPE_PARTIAL,
        Household,
    )

    return Household.objects.exclude(collect_individual_data__in=[COLLECT_TYPE_FULL, COLLECT_TYPE_PARTIAL]).update(
        children_count=Coalesce("female_age_group_0_5_count", 0)
        + Coalesce("female_age_group_6_11_count", 0)
        + Coalesce("female_age_group_12_17_count", 0)
        + Coalesce("male_age_group_0_5_count", 0)
        + Coalesce("male_age_group_6_11_count", 0)
        + Coalesce("male_age_group_12_17_count", 0),
        female_children_count=Coalesce("female_age_group_0_5_count", 0)
        + Coalesce("female_age_group_6_11_count", 0)
        + Coalesce("female_age_group_12_17_count", 0),
        male_children_count=Coalesce("male_age_group_0_5_count", 0)
        + Coalesce("male_age_group_6_11_count", 0)
        + Coalesce("male_age_group_12_17_count", 0),
        children_disabled_count=Coalesce("female_age_group_0_5_disabled_count", 0)
        + Coalesce("female_age_group_6_11_disabled_count", 0)
        + Coalesce("female_age_group_12_17_disabled_count", 0)
        + Coalesce("male_age_group_0_5_disabled_count", 0)
        + Coalesce("male_age_group_6_11_disabled_count", 0)
        + Coalesce("male_age_group_12_17_disabled_count", 0),
        female_children_disabled_count=Coalesce("female_age_group_0_5_disabled_count", 0)
        + Coalesce("female_age_group_6_11_disabled_count", 0)
        + Coalesce("female_age_group_12_17_disabled_count", 0),
        male_children_disabled_count=Coalesce("male_age_group_0_5_disabled_count", 0)
        + Coalesce("male_age_group_6_11_disabled_count", 0)
        + Coalesce("male_age_group_12_17_disabled_count", 0),
    )


@app.task()
@sentry_tags
def update_individuals_iban_from_xlsx_task(xlsx_update_file_id: UUID, uploaded_by_id: UUID) -> None:
    from hct_mis_api.apps.account.models import User
    from hct_mis_api.apps.household.models import XlsxUpdateFile
    from hct_mis_api.apps.household.services.individuals_iban_xlsx_update import (
        IndividualsIBANXlsxUpdate,
    )

    uploaded_by = User.objects.get(id=uploaded_by_id)
    try:
        xlsx_update_file = XlsxUpdateFile.objects.get(id=xlsx_update_file_id)
        with configure_scope() as scope:
            scope.set_tag("business_area", xlsx_update_file.business_area)
            updater = IndividualsIBANXlsxUpdate(xlsx_update_file)
            updater.validate()
            if updater.validation_errors:
                updater.send_failure_email()
                return

            updater.update()
            updater.send_success_email()

    except Exception as e:
        IndividualsIBANXlsxUpdate.send_error_email(
            error_message=str(e), xlsx_update_file_id=str(xlsx_update_file_id), uploaded_by=uploaded_by
        )
