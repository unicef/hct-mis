from environ.environ import Env

DEFAULTS = {
    "ENV": (str, "dev"),
    "DOMAIN": (str, "localhost"),
    "DJANGO_ALLOWED_HOSTS": (list, "*"),
    "HCT_MIS_FRONTEND_HOST": (str, ""),
    "ALERTS_EMAIL": (str, "admin@hct-mis.com"),
    "SECRET_KEY": (str, ""),
    "DATA_VOLUME": (str, "/data"),
    "HCT_MIS_UPLOADS_PATH": (str, ""),
    "DEFAULT_FROM_EMAIL": (str, "HCT-MIS Stage <noreply@hct-mis.org>"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_PORT": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_USE_TLS": (bool, True),
    "KOBO_KF_URL": (str, "https://kf-hope.unitst.org"),
    "KOBO_KC_URL": (str, "https://kc-hope.unitst.org"),
    "KOBO_MASTER_API_TOKEN": (str, "KOBO_TOKEN"),
    "AZURE_CLIENT_ID": (str, ""),
    "AZURE_CLIENT_SECRET": (str, ""),
    "AZURE_TENANT_KEY": (str, ""),
    "SANCTION_LIST_CC_MAIL": (str, "dfam-cashassistance@unicef.org"),
    "ELASTICSEARCH_HOST": (str, "elasticsearch:9200"),
    "RAPID_PRO_URL": (str, "https://rapidpro.io"),
    "DATAMART_USER": (str, ""),
    "DATAMART_URL": (str, "https://datamart-dev.unicef.io"),
    "DATAMART_PASSWORD": (str, ""),
    "POWER_QUERY_DB_ALIAS": (str, "read_only"),
    "ROOT_ACCESS_TOKEN": (str, ""),
    "SENTRY_DSN": (str, ""),
    "SENTRY_URL": (str, ""),
    "SENTRY_ENVIRONMENT": (str, ""),
    "CELERY_BROKER_URL": (str, ""),
    "CELERY_RESULT_BACKEND": (str, ""),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False),
    "ADMIN_PANEL_URL": (str, "unicorn"),
}

env = Env(**DEFAULTS)
