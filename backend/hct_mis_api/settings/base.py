from __future__ import absolute_import

import logging
import os
import sys

####
# Change per project
####
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import SelectMultiple
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

PROJECT_NAME = "hct_mis_api"
# project root and add "apps" to the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# domains/hosts etc.
DOMAIN_NAME = os.getenv("DOMAIN", "localhost")
WWW_ROOT = "http://%s/" % DOMAIN_NAME
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") + [DOMAIN_NAME]
FRONTEND_HOST = os.getenv("HCT_MIS_FRONTEND_HOST", DOMAIN_NAME)

####
# Other settings
####
ADMINS = (
    ("Alerts", os.getenv("ALERTS_EMAIL") or "admin@hct-mis.com"),
    ("Tivix", f"unicef-hct-mis+{slugify(DOMAIN_NAME)}@tivix.com"),
)

SITE_ID = 1
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
SECRET_KEY = os.getenv("SECRET_KEY")
DEFAULT_CHARSET = "utf-8"
ROOT_URLCONF = "hct_mis_api.urls"

DATA_VOLUME = os.getenv("DATA_VOLUME", "/data")

ALLOWED_EXTENSIONS = (
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "img",
    "png",
    "jpg",
    "jpeg",
    "csv",
    "zip",
)
UPLOADS_DIR_NAME = "uploads"
MEDIA_URL = f"/api/{UPLOADS_DIR_NAME}/"
MEDIA_ROOT = os.getenv("HCT_MIS_UPLOADS_PATH", os.path.join(DATA_VOLUME, UPLOADS_DIR_NAME))

FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25mb
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# static resources related. See documentation at: http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_URL = "/api/static/"
STATIC_ROOT = f"{DATA_VOLUME}/staticserve"

# static serving
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

DEBUG = True
IS_DEV = False
IS_STAGING = False
IS_PROD = False

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "HCT-MIS Stage <noreply@hct-mis.org>")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "").lower() == "true"

# Get the ENV setting. Needs to be set in .bashrc or similar.
ENV = os.getenv("ENV")
if not ENV:
    raise Exception("Environment variable ENV is required!")

# prefix all non-production emails
if ENV != "prod":
    EMAIL_SUBJECT_PREFIX = "{}".format(ENV)

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": 5432,
    },
    "cash_assist_datahub_mis": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "OPTIONS": {"options": "-c search_path=mis"},
        "NAME": os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST"),
        "PORT": 5432,
    },
    "cash_assist_datahub_ca": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "OPTIONS": {"options": "-c search_path=ca"},
        "NAME": os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST"),
        "PORT": 5432,
    },
    "cash_assist_datahub_erp": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "OPTIONS": {"options": "-c search_path=erp"},
        "NAME": os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST"),
        "PORT": 5432,
    },
    "registration_datahub": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("POSTGRES_REGISTRATION_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_REGISTRATION_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_REGISTRATION_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_REGISTRATION_DATAHUB_HOST"),
        "PORT": 5432,
    },
}

# If app is not specified here it will use default db
DATABASE_APPS_MAPPING = {
    "cash_assist_datahub": "cash_assist_datahub_ca",
    "mis_datahub": "cash_assist_datahub_mis",
    "erp_datahub": "cash_assist_datahub_erp",
    "registration_datahub": "registration_datahub",
}

DATABASE_ROUTERS = ("hct_mis_api.apps.core.dbrouters.DbRouter",)

POSTGRES_SSL_MODE = os.getenv("POSTGRES_SSL_MODE", "off")
if POSTGRES_SSL_MODE == "on":
    DATABASES["default"].update({"OPTIONS": {"sslmode": "require"}})

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "hct_mis_api.middlewares.sentry.SentryScopeMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                # Social auth context_processors
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]
PROJECT_APPS = [
    "hct_mis_api.apps.account",
    "hct_mis_api.apps.core",
    "hct_mis_api.apps.grievance",
    "hct_mis_api.apps.household",
    "hct_mis_api.apps.id_management",
    "hct_mis_api.apps.intervention",
    "hct_mis_api.apps.payment",
    "hct_mis_api.apps.program",
    # "hct_mis_api.apps.targeting",
    "hct_mis_api.apps.targeting.apps.TargetingConfig",
    "hct_mis_api.apps.utils",
    "hct_mis_api.apps.registration_datahub",
    "hct_mis_api.apps.registration_data",
    "hct_mis_api.apps.cash_assist_datahub",
    "hct_mis_api.apps.mis_datahub",
    "hct_mis_api.apps.erp_datahub",
    "hct_mis_api.apps.sanction_list",
    "hct_mis_api.apps.steficon",
    "hct_mis_api.apps.reporting",
    "hct_mis_api.apps.activity_log",
]

DJANGO_APPS = [
    # "django.contrib.admin",
    "smart_admin.templates",
    "smart_admin",
    "django.contrib.auth",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

OTHER_APPS = [
    "django_countries",
    "phonenumber_field",
    "compressor",
    "graphene_django",
    "social_django",
    "corsheaders",
    "django_elasticsearch_dsl",
    "constance",
    "admin_extra_urls",
    "adminfilters",
    "multiselectfield",
    "mptt",
    "django_extensions",
]

INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + PROJECT_APPS

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_RESET_TIMEOUT_DAYS = 31

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
]

NOSE_ARGS = ["--with-timer", "--nocapture", "--nologcapture"]


# helper function to extend all the common lists
def extend_list_avoid_repeats(list_to_extend, extend_with):
    """Extends the first list with the elements in the second one, making sure its elements are not already there in the
    original list."""
    list_to_extend.extend(filter(lambda x: not list_to_extend.count(x), extend_with))


LOG_LEVEL = "DEBUG" if DEBUG and "test" not in sys.argv else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s line %(lineno)d: %(message)s"},
        "verbose": {
            "format": "[%(asctime)s][%(levelname)s][%(name)s] %(filename)s.%(funcName)s:%(lineno)d %(message)s",
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "default": {"level": LOG_LEVEL, "class": "logging.StreamHandler", "formatter": "standard"},
        "file": {"level": LOG_LEVEL, "class": "logging.FileHandler", "filename": "debug.log"},
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO", "propagate": True},
        "console": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "django.request": {"handlers": ["default"], "level": "ERROR", "propagate": False},
        "django.security.DisallowedHost": {
            # Skip "SuspiciousOperation: Invalid HTTP_HOST" e-mails.
            "handlers": ["default"],
            "propagate": False,
        },
        "elasticsearch": {"handlers": ["file"], "level": "CRITICAL", "propagate": True},
    },
}

GIT_VERSION = os.getenv("GIT_VERSION", "UNKNOWN")

REDIS_INSTANCE = os.getenv("REDIS_INSTANCE", "redis")

if REDIS_INSTANCE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_INSTANCE}/1",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "TIMEOUT": 3600,
        }
    }
    DJANGO_REDIS_IGNORE_EXCEPTIONS = not DEBUG
else:
    CACHES = {"default": {"BACKEND": "common.cache_backends.DummyRedisCache", "LOCATION": "hct_mis"}}

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
AUTH_USER_MODEL = "account.User"

GRAPHENE = {
    "SCHEMA": "hct_mis_api.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
}

# Social Auth settings.
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_KEY = os.environ.get("AZURE_TENANT_KEY")
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = AZURE_CLIENT_ID
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = AZURE_CLIENT_SECRET
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = AZURE_TENANT_KEY
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
]
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_PIPELINE = (
    "hct_mis_api.apps.account.authentication.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "hct_mis_api.apps.account.authentication.require_email",
    "social_core.pipeline.social_auth.associate_by_email",
    "hct_mis_api.apps.account.authentication.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "hct_mis_api.apps.account.authentication.user_details",
)
SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_USER_FIELDS = [
    "email",
    "fullname",
]

SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SCOPE = [
    "openid",
    "email",
    "profile",
]

SOCIAL_AUTH_SANITIZE_REDIRECTS = True

LOGIN_URL = "/api/login/azuread-tenant-oauth2"

TEST_RUNNER = "hct_mis_api.apps.core.mis_test_runner.PostgresTestRunner"

GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

PHONENUMBER_DEFAULT_REGION = "US"

AIRFLOW_HOST = "airflow_webserver"

SANCTION_LIST_CC_MAIL = os.getenv("SANCTION_LIST_CC_MAIL", "dfam-cashassistance@unicef.org")

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch:9200")

RAPID_PRO_URL = os.getenv("RAPID_PRO_URL", "https://rapidpro.io")

# DJANGO CONSTANCE settings
CONSTANCE_REDIS_CONNECTION = f"redis://{REDIS_INSTANCE}/0"

CONSTANCE_ADDITIONAL_FIELDS = {
    "percentages": (
        "django.forms.fields.IntegerField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0), MaxValueValidator(100)]},
    ),
    "positive_integers": (
        "django.forms.fields.IntegerField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0)]},
    ),
    "positive_floats": (
        "django.forms.fields.FloatField",
        {"widget": "django.forms.widgets.NumberInput", "validators": [MinValueValidator(0)]},
    ),
}

CONSTANCE_CONFIG = {
    # BATCH SETTINGS
    "DEDUPLICATION_BATCH_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    # "DEDUPLICATION_BATCH_MIN_SCORE": (
    #     15.0,
    #     "Results below the minimum score will not be taken into account",
    #     "positive_integers",
    # ),
    "DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    # GOLDEN RECORDS SETTINGS
    "DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE": (
        6.0,
        "Results below the minimum score will not be taken into account",
        "positive_floats",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE": (
        11.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    # SANCTION LIST
    "SANCTION_LIST_MATCH_SCORE": (
        4.8,
        "Results equal or above this score are considered possible matches",
        "positive_floats",
    ),
    # RAPID PRO
    "RAPID_PRO_PROVIDER": ("tel", "Rapid pro messages provider (telegram/tel)"),
    # CASH ASSIST
    "CASH_ASSIST_URL_PREFIX": ("", "Cash Assist base url used to generate url to cash assist"),
}

CONSTANCE_DBS = ("default",)

# MICROSOFT GRAPH
AZURE_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
AZURE_GRAPH_API_VERSION = "v1.0"
AZURE_TOKEN_URL = "https://login.microsoftonline.com/unicef.org/oauth2/token"

TEST_OUTPUT_DIR = "./test-results"
TEST_OUTPUT_FILE_NAME = "result.xml"

DATAMART_USER = os.getenv("DATAMART_USER")
DATAMART_PASSWORD = os.getenv("DATAMART_PASSWORD")
DATAMART_URL = os.getenv("DATAMART_URL", "https://datamart-dev.unicef.io")

KOBO_MASTER_API_TOKEN = os.getenv("KOBO_MASTER_API_TOKEN", "KOBO_TOKEN")

COUNTRIES_OVERRIDE = {
    "U": {
        "name": _("Unknown or Not Applicable"),
        "alpha3": "U",
        "ioc_code": "U",
    },
}

SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from hct_mis_api import get_full_version

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(transaction_style='url'),
                      sentry_logging,
                      # RedisIntegration(),
                      # CeleryIntegration()
                      ],
        release=get_full_version(),
        send_default_pii=True
    )

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"https://\w+.blob.core.windows.net$"
]

SMART_ADMIN_SECTIONS = {
    'Security': ['account',
                 'auth'
                 ],
    'Rule Engine': ['steficon',
                 ],
    'Logs': ['admin.LogEntry',
             ],
    'Grievance': ['grievance'],
    'Kobo': ['core.FlexibleAttributeChoice',
             'core.XLSXKoboTemplate',
             'core.FlexibleAttribute',
             'core.FlexibleAttributeGroup',
             ],
    'HUBs': ['cash_assist_datahub',
             'erp_datahub',
             'mis_datahub',
             'registration_datahub',
             ],
    'System': [
        'social_django',
        'constance',
        'sites',
    ],
    'Other': [],
    '_hidden_': []
}
