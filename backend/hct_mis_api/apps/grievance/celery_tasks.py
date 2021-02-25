from hct_mis_api.apps.core.celery import app


@app.task
def deduplicate_and_check_against_sanctions_list_task(
    should_populate_index, registration_data_import_id, individuals_ids
):
    from hct_mis_api.apps.grievance.tasks.deduplicate_and_check_sanctions import (
        DeduplicateAndCheckAgainstSanctionsListTask,
    )

    DeduplicateAndCheckAgainstSanctionsListTask().execute(
        should_populate_index, registration_data_import_id, individuals_ids
    )
