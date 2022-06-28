import logging
from uuid import UUID

from concurrency.api import disable_concurrency

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.household.services.household_recalculate_data import recalculate_data

logger = logging.getLogger(__name__)


@app.task()
def recalculate_population_fields_task(household_ids: list[UUID] = None):
    logger.info("recalculate_population_fields")
    try:
        from hct_mis_api.apps.household.models import YES, Household, Individual

        params = {"collect_individual_data": YES}

        if household_ids:
            params["pk__in"] = household_ids

        for hh in (
            Household.objects.filter(**params)
            .only("id", "collect_individual_data")
            .prefetch_related("individuals")
            .iterator(chunk_size=10000)
        ):
            with disable_concurrency(Household):
                with disable_concurrency(Individual):
                    recalculate_data(hh)

    except Exception as e:
        logger.exception(e)
        raise

    logger.info("recalculate_population_fields end")


@app.task()
def calculate_children_fields_for_not_collected_individual_data():
    from hct_mis_api.apps.household.models import Household
    from django.db.models import F

    Household.objects.update(
        children_count=F("female_age_group_0_5_count")
        + F("female_age_group_6_11_count")
        + F("female_age_group_12_17_count")
        + F("male_age_group_0_5_count")
        + F("male_age_group_6_11_count")
        + F("male_age_group_12_17_count"),
        female_children_count=F("female_age_group_0_5_count")
        + F("female_age_group_6_11_count")
        + F("female_age_group_12_17_count"),
        male_children_count=F("male_age_group_0_5_count")
        + F("male_age_group_6_11_count")
        + F("male_age_group_12_17_count"),
        children_disabled_count=F("female_age_group_0_5_disabled_count")
        + F("female_age_group_6_11_disabled_count")
        + F("female_age_group_12_17_disabled_count")
        + F("male_age_group_0_5_disabled_count")
        + F("male_age_group_6_11_disabled_count")
        + F("male_age_group_12_17_disabled_count"),
        female_children_disabled_count=F("female_age_group_0_5_disabled_count")
        + F("female_age_group_6_11_disabled_count")
        + F("female_age_group_12_17_disabled_count"),
        male_children_disabled_count=F("male_age_group_0_5_disabled_count")
        + F("male_age_group_6_11_disabled_count")
        + F("male_age_group_12_17_disabled_count"),
    )


@app.task()
def update_individuals_iban_from_xlsx_task(xlsx_update_file_id: UUID, uploaded_by_id: UUID):
    from hct_mis_api.apps.household.models import XlsxUpdateFile
    from hct_mis_api.apps.household.services.individuals_iban_xlsx_update import IndividualsIBANXlsxUpdate
    from hct_mis_api.apps.account.models import User

    logger.info("update_individuals_iban_from_xlsx_task start")
    uploaded_by = User.objects.get(id=uploaded_by_id)
    try:
        xlsx_update_file = XlsxUpdateFile.objects.get(id=xlsx_update_file_id)
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

    logger.info("update_individuals_iban_from_xlsx_task end")
