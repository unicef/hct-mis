from environ import Env

DEFAULTS = {
    "AURORA_SERVER": (str, ""),
    "AURORA_TOKEN": (str, ""),
    "AURORA_USER": (str, ""),
    "DEBUG": (bool, False),
    "ENV": (str, "dev"),
    "DOMAIN": (str, "localhost:8000"),
    "DJANGO_ALLOWED_HOSTS": (list, "*"),
    "HCT_MIS_FRONTEND_HOST": (str, ""),
    "ALERTS_EMAIL": (str, "admin@hct-mis.com"),
    "SECRET_KEY": (str, ""),
    "DATA_VOLUME": (str, "/data"),
    "HCT_MIS_UPLOADS_PATH": (str, ""),
    "DEFAULT_FROM_EMAIL": (str, "HOPE Stage <hope@mail.unicef.org>"),
    "EMAIL_BACKEND": (str, "django.core.mail.backends.smtp.EmailBackend"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_PORT": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_USE_TLS": (bool, True),
    "MAILJET_API_KEY": (str, ""),
    "MAILJET_SECRET_KEY": (str, ""),
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
    "SENTRY_ENABLE_TRACING": (bool, False),
    "CELERY_BROKER_URL": (str, ""),
    "CELERY_RESULT_BACKEND": (str, ""),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False),
    "ADMIN_PANEL_URL": (str, "unicorn"),
    "SESSION_COOKIE_SECURE": (bool, True),
    "SESSION_COOKIE_HTTPONLY": (bool, True),
    "CSRF_COOKIE_HTTPONLY": (bool, True),
    "CSRF_COOKIE_SECURE": (bool, True),
    "SECURE_CONTENT_TYPE_NOSNIFF": (bool, True),
    "SECURE_REFERRER_POLICY": (str, "same-origin"),
    "SESSION_COOKIE_NAME": (str, "sessionid"),
    "SECURE_HSTS_SECONDS": (int, 3600),
    "FLOWER_ADDRESS": (str, "https://hope.unicef.org/flower"),
    "CACHE_ENABLED": (bool, True),
    "CSP_REPORT_URI": (tuple, ("",)),
    "CSP_REPORT_ONLY": (bool, True),
    "CSP_REPORT_PERCENTAGE": (float, 0.1),
    "CSP_DEFAULT_SRC": (tuple, ("'self'",)),
    "CSP_FRAME_ANCESTORS": (tuple, ("'none'",)),
    "CSP_STYLE_SRC": (
        tuple,
        (
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ),
    ),
    "CSP_MANIFEST_SRC": (tuple, ("'self'",)),
    "CSP_SCRIPT_SRC": (
        tuple,
        (
            "'self'",
            "'unsafe-inline'",
            "'unsafe-eval'",
        ),
    ),
    "CSP_IMG_SRC": (
        tuple,
        (
            "'self'",
            "data:",
        ),
    ),
    "CSP_FONT_SRC": (
        tuple,
        (
            "'self'",
            "data:",
            "fonts.gstatic.com",
            "maxcdn.bootstrapcdn.com",
        ),
    ),
    "CSP_MEDIA_SRC": (tuple, ("'self'",)),
    "CSP_CONNECT_SRC": (
        tuple,
        (
            "gov-bam.nr-data.net",
            "cdn.jsdelivr.net",
        ),
    ),
    "MATOMO_TRACKER_URL": (
        str,
        "https://unisitetracker.unicef.io/",
    ),
    "MATOMO_SCRIPT_URL": (
        str,
        "",
    ),
    "MATOMO_SITE_ID": (
        str,
        "",
    ),
}

env = Env(**DEFAULTS)
