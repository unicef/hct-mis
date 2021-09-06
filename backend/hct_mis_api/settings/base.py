from __future__ import absolute_import

import logging
import os
import re
import sys
from pathlib import Path
from uuid import uuid4

####
# Change per project
####
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import SelectMultiple
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from sentry_sdk.integrations.celery import CeleryIntegration
from single_source import get_version

from hct_mis_api.apps.core.tasks_schedules import TASKS_SCHEDULES

PROJECT_NAME = "hct_mis_api"
# project root and add "apps" to the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from .config import env

# domains/hosts etc.
DOMAIN_NAME = env("DOMAIN")
WWW_ROOT = "http://%s/" % DOMAIN_NAME
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[DOMAIN_NAME])
FRONTEND_HOST = env("HCT_MIS_FRONTEND_HOST", default=DOMAIN_NAME)

####
# Other settings
####
ADMINS = (
    ("Alerts", env("ALERTS_EMAIL")),
    ("Tivix", f"unicef-hct-mis+{slugify(DOMAIN_NAME)}@tivix.com"),
)

SITE_ID = 1
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = True
SECRET_KEY = env("SECRET_KEY")
DEFAULT_CHARSET = "utf-8"
ROOT_URLCONF = "hct_mis_api.urls"

DATA_VOLUME = env("DATA_VOLUME")

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
MEDIA_ROOT = env("HCT_MIS_UPLOADS_PATH") or os.path.join(DATA_VOLUME, UPLOADS_DIR_NAME)

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

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# EMAIL_CONFIG = env.email_url('EMAIL_URL', default='smtp://user@:password@localhost:25')
# vars().update(EMAIL_CONFIG)

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")

KOBO_KF_URL = env("KOBO_KF_URL")
KOBO_KC_URL = env("KOBO_KC_URL")
KOBO_MASTER_API_TOKEN = env("KOBO_MASTER_API_TOKEN")

# Get the ENV setting. Needs to be set in .bashrc or similar.
ENV = env("ENV")

# prefix all non-production emails
if ENV != "prod":
    EMAIL_SUBJECT_PREFIX = "{}".format(ENV)

# BACKWARD_COMPATIBILITY SNIPPET
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = (
        f'postgis://{os.getenv("POSTGRES_USER")}'
        f':{os.getenv("POSTGRES_PASSWORD")}'
        f'@{os.getenv("POSTGRES_HOST")}:5432/'
        f'{os.getenv("POSTGRES_DB")}'
    )
    if os.getenv("POSTGRES_SSL_MODE", "off") == "on":
        os.environ["DATABASE_URL"] = os.environ["DATABASE_URL"] + "?sslmode=require"

if "DATABASE_URL_HUB_MIS" not in os.environ:
    os.environ["DATABASE_URL_HUB_MIS"] = (
        f'postgis://{os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER")}'
        f':{os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD")}'
        f'@{os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST")}:5432/'
        f'{os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB")}?options=-c search_path=mis'
    )
if "DATABASE_URL_HUB_CA" not in os.environ:
    os.environ["DATABASE_URL_HUB_CA"] = (
        f'postgis://{os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER")}'
        f':{os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD")}'
        f'@{os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST")}:5432/'
        f'{os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB")}?options=-c search_path=ca'
    )
if "DATABASE_URL_HUB_ERP" not in os.environ:
    os.environ["DATABASE_URL_HUB_ERP"] = (
        f'postgis://{os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER")}'
        f':{os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD")}'
        f'@{os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST")}:5432/'
        f'{os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB")}?options=-c search_path=erp'
    )
if "DATABASE_URL_HUB_REGISTRATION" not in os.environ:
    os.environ["DATABASE_URL_HUB_REGISTRATION"] = (
        f'postgis://{os.getenv("POSTGRES_REGISTRATION_DATAHUB_USER")}'
        f':{os.getenv("POSTGRES_REGISTRATION_DATAHUB_PASSWORD")}'
        f'@{os.getenv("POSTGRES_REGISTRATION_DATAHUB_HOST")}:5432/'
        f'{os.getenv("POSTGRES_REGISTRATION_DATAHUB_DB")}'
    )
os.environ["DATABASE_URL_BACKUP"] = (
    f'postgis://hctappprdusr@pgsql-10-reserved-hctmis-prd-restore090321'
    f':{os.getenv("POSTGRES_PASSWORD")}'
    f'@pgsql-10-reserved-hctmis-prd-restore090321.postgres.database.azure.com:5432/'
    f'{os.getenv("POSTGRES_DB")}'
)

DATABASES = {
    "default": env.db(),
    "cash_assist_datahub_mis": env.db("DATABASE_URL_HUB_MIS"),
    "cash_assist_datahub_ca": env.db("DATABASE_URL_HUB_CA"),
    "cash_assist_datahub_erp": env.db("DATABASE_URL_HUB_ERP"),
    "registration_datahub": env.db("DATABASE_URL_HUB_REGISTRATION"),
    "backup_database": env.db("DATABASE_URL_BACKUP")
}

# If app is not specified here it will use default db
DATABASE_APPS_MAPPING = {
    "cash_assist_datahub": "cash_assist_datahub_ca",
    "mis_datahub": "cash_assist_datahub_mis",
    "erp_datahub": "cash_assist_datahub_erp",
    "registration_datahub": "registration_datahub",
    "grievance2": "backup_database",
}

DATABASE_ROUTERS = ("hct_mis_api.apps.core.dbrouters.DbRouter",)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "hct_mis_api.middlewares.sentry.SentryScopeMiddleware",
    "hct_mis_api.middlewares.version.VersionMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_ROOT, "apps", "administration", "templates"),
            os.path.join(PROJECT_ROOT, "apps", "core", "templates"),
        ],
        "OPTIONS": {
            "loaders": ["django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader"],
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
    "hct_mis_api.apps.core.apps.CoreConfig",
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
    "hct_mis_api.apps.grievance2",
]

DJANGO_APPS = [
    # "hct_mis_api.apps.administration.apps.TemplateConfig",
    # "smart_admin.templates",
    "advanced_filters",
    "smart_admin.logs",
    "smart_admin.apps.SmartTemplateConfig",
    "hct_mis_api.apps.administration.apps.Config",
    # "smart_admin",
    "django_sysinfo",
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
    "jsoneditor",
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
    "adminactions",
    "multiselectfield",
    "mptt",
    "django_extensions",
    "django_celery_results",
    "django_celery_beat",
    "explorer",
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

# REDIS_INSTANCE = os.getenv("REDIS_INSTANCE", "redis")
#
# if REDIS_INSTANCE:
#     CACHES = {
#         "default": {
#             "BACKEND": "django_redis.cache.RedisCache",
#             "LOCATION": f"redis://{REDIS_INSTANCE}/1",
#             "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#             "TIMEOUT": 3600,
#         }
#     }
#     DJANGO_REDIS_IGNORE_EXCEPTIONS = not DEBUG
# else:
#     CACHES = {"default": {"BACKEND": "common.cache_backends.DummyRedisCache", "LOCATION": "hct_mis"}}

REDIS_INSTANCE = os.getenv("REDIS_INSTANCE", "redis:6379")
if "CACHE_URL" not in os.environ:
    if REDIS_INSTANCE:
        os.environ["CACHE_URL"] = f"redis://{REDIS_INSTANCE}/1?client_class=django_redis.client.DefaultClient"
    else:
        os.environ["CACHE_URL"] = f"dummycache://{REDIS_INSTANCE}/1?client_class=django_redis.client.DefaultClient"

CACHES = {
    "default": env.cache(),
}

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
AUTH_USER_MODEL = "account.User"

GRAPHENE = {
    "SCHEMA": "hct_mis_api.schema.schema",
    "SCHEMA_OUTPUT": "schema.json",
    "SCHEMA_INDENT": 2,
}

# Social Auth settings.
AZURE_CLIENT_ID = env("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = env("AZURE_CLIENT_SECRET")
AZURE_TENANT_KEY = env("AZURE_TENANT_KEY")
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

SANCTION_LIST_CC_MAIL = env("SANCTION_LIST_CC_MAIL")

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")

RAPID_PRO_URL = env("RAPID_PRO_URL")

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
    "DEDUPLICATION_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered duplicates",
        "positive_floats",
    ),
    "DEDUPLICATION_POSSIBLE_DUPLICATE_SCORE": (
        6.0,
        "Results equal or above this score are considered possible duplicates (needs adjudication) must be lower than DEDUPLICATION_DUPLICATE_SCORE",
        "positive_floats",
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE": (
        50,
        "If percentage of duplicates is higher or equal to this setting, deduplication is aborted",
        "percentages",
    ),
    "CASHASSIST_DOAP_RECIPIENT": ("", "UNHCR email address where to send DOAP updates", str),
    "KOBO_ADMIN_CREDENTIALS": (
        "",
        "Kobo superuser credentislas in format user:password",
        str,
    ),
    "DEDUPLICATION_BATCH_DUPLICATES_ALLOWED": (
        5,
        "If amount of duplicates for single individual exceeds this limit deduplication is aborted",
        "positive_integers",
    ),
    "KOBO_APP_API_TOKEN": ("", "Kobo KPI token", str),
    # GOLDEN RECORDS SETTINGS
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
    "SEND_GRIEVANCES_NOTIFICATION": (
        False,
        "Should send grievances notification",
        bool,
    ),
    "IGNORED_USER_LINKED_OBJECTS": (
        "created_advanced_filters,advancedfilter,logentry,social_auth,query,querylog,logs",
        "list of relation to hide in 'linked objects' user page",
        str,
    ),
    "QUICK_LINKS": (
        """Kobo,https://kf-hope.unitst.org/;
CashAssist,https://cashassist-trn.crm4.dynamics.com/;
Sentry,https://excubo.unicef.io/sentry/hct-mis-stg/;
elasticsearch,hope-elasticsearch-coordinating-only:9200;
Datamart,https://datamart.unicef.io;
Flower,https://stg-hope.unitst.org/flower/;
Azure,https://unicef.visualstudio.com/ICTD-HCT-MIS/;
""",
        "",
        str,
    ),
}

CONSTANCE_DBS = ("default",)

# MICROSOFT GRAPH
AZURE_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
AZURE_GRAPH_API_VERSION = "v1.0"
AZURE_TOKEN_URL = "https://login.microsoftonline.com/unicef.org/oauth2/token"

TEST_OUTPUT_DIR = "./test-results"
TEST_OUTPUT_FILE_NAME = "result.xml"

DATAMART_USER = env("DATAMART_USER")
DATAMART_PASSWORD = env("DATAMART_PASSWORD")
DATAMART_URL = env("DATAMART_URL")

COUNTRIES_OVERRIDE = {
    "U": {
        "name": _("Unknown or Not Applicable"),
        "alpha3": "U",
        "ioc_code": "U",
    },
}

ROOT_TOKEN = env.str("ROOT_ACCESS_TOKEN", uuid4().hex)

SENTRY_DSN = env("SENTRY_DSN")
SENTRY_URL = env("SENTRY_URL")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    from hct_mis_api import get_full_version

    sentry_logging = LoggingIntegration(
        level=logging.INFO, event_level=logging.ERROR  # Capture info and above as breadcrumbs  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            sentry_logging,
            CeleryIntegration()
            # RedisIntegration(),
        ],
        release=get_full_version(),
        send_default_pii=True,
    )

CORS_ALLOWED_ORIGIN_REGEXES = [r"https://\w+.blob.core.windows.net$"]

CELERY_BROKER_URL = (f"redis://{REDIS_INSTANCE}/0",)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = f"redis://{REDIS_INSTANCE}/0"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULE = TASKS_SCHEDULES
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER")

from smart_admin.utils import match, regex

SMART_ADMIN_SECTIONS = {
    "HOPE": [
        "program",
        match("household.H*"),
        regex(r"household\.I.*"),
        "targeting",
        "payment",
    ],
    "Grievance": ["grievance"],
    "Configuration": ["core", "constance", "household", "household.agency"],
    "Rule Engine": [
        "steficon",
    ],
    "Security": ["account", "auth"],
    "Logs": [
        "admin.LogEntry",
    ],
    "Kobo": [
        "core.FlexibleAttributeChoice",
        "core.XLSXKoboTemplate",
        "core.FlexibleAttribute",
        "core.FlexibleAttributeGroup",
    ],
    "HUBs": [
        "cash_assist_datahub",
        "erp_datahub",
        "mis_datahub",
        "registration_datahub",
    ],
    "System": [
        "social_django",
        "constance",
        "sites",
    ],
}

# SMART_ADMIN_BOOKMARKS = [('GitHub', 'https://github.com/saxix/django-smart-admin'),
#                          'https://github.com/saxix/django-adminactions',
#                          'https://github.com/saxix/django-sysinfo',
#                          'https://github.com/saxix/django-adminfilters',
#                          'https://github.com/saxix/django-admin-extra-urls',
#                          ]
SMART_ADMIN_BOOKMARKS = "hct_mis_api.apps.administration.site.get_bookmarks"

SMART_ADMIN_BOOKMARKS_PERMISSION = None
SMART_ADMIN_PROFILE_LINK = True
SMART_ADMIN_ISROOT = lambda r, *a: r.user.is_superuser and r.headers.get("x-root-token") == env("ROOT_TOKEN")

EXCHANGE_RATE_CACHE_EXPIRY = 1 * 60 * 60 * 24

VERSION = get_version(__name__, Path(PROJECT_ROOT).parent, default_return=None)

# see adminactions.perms
# set handker to AA_PERMISSION_CREATE_USE_COMMAND
AA_PERMISSION_HANDLER = 3


def filter_environment(key):
    return False


SYSINFO = {
    "filter_environment": "hct_mis_api.settings.base.filter_environment",
    "ttl": 60,
}

EXPLORER_CONNECTIONS = {
    "default": "default",
    "HUB MIS": "cash_assist_datahub_mis",
    "HUB CA": "cash_assist_datahub_ca",
    "HUB ERP": "cash_assist_datahub_erp",
    "HUB Reg": "registration_datahub",
}
EXPLORER_DEFAULT_CONNECTION = "default"
EXPLORER_PERMISSION_VIEW = lambda r: r.user.is_superuser
EXPLORER_PERMISSION_CHANGE = lambda r: r.user.is_superuser

# EXPLORER_SCHEMA_INCLUDE_TABLE_PREFIXES = (
#     'hct_mis_api',
# )
# EXPLORER_SCHEMA_EXCLUDE_TABLE_PREFIXES = (
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django_site',
#     'django_session',
#     'django.contrib.sessions',
#     'django.contrib.admin',
#     'django_celery',
#     'django_celery.beat',
#     'django_celery_beat',
#     'django_celery_results',
#     'django_migrations',
#     'social_auth',
#     'django_admin',
# )
