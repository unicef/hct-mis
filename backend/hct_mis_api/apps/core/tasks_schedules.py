from celery.schedules import crontab

TASKS_SCHEDULES = {
    "sync_sanction_list": {
        "task": "hct_mis_api.apps.sanction_list.celery_tasks.sync_sanction_list_task",
        "schedule": crontab(minute=0, hour=0),
    },
    "pull_from_erp_datahub": {
        "task": "hct_mis_api.apps.erp_datahub.celery_tasks.pull_from_erp_datahub_task",
        "schedule": crontab(minute="*/30"),
    },
    "pull_from_erp_dh": {
        "task": "hct_mis_api.apps.cash_assist_datahub.celery_tasks.pull_from_erp_dh_task",
        "schedule": crontab(minute=0, hour="*/1"),
    },
    "get_sync_run_rapid_pro": {
        "task": "hct_mis_api.apps.payment.celery_tasks.get_sync_run_rapid_pro_task",
        "schedule": crontab(minute="*/20"),
    },
}
