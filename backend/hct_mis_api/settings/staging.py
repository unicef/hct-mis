from __future__ import absolute_import

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: ignore=F403

# dev overrides
DEBUG = False
IS_STAGING = True

# domains/hosts etc.
DOMAIN_NAME = os.getenv("DOMAIN", "dev-hct.unitst.org")
WWW_ROOT = "http://%s/" % DOMAIN_NAME

# other
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CACHE
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "TIMEOUT": 1800}}

# STORAGE
STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"

AZURE_ACCOUNT_NAME = os.getenv("STORAGE_AZURE_ACCOUNT_NAME", "")
AZURE_ACCOUNT_KEY = os.getenv("STORAGE_AZURE_ACCOUNT_KEY", "")
AZURE_URL_EXPIRATION_SECS = 10800

AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"

DEFAULT_FILE_STORAGE = "core.storage.AzureMediaStorage"
STATICFILES_STORAGE = "core.storage.AzureStaticStorage"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

if os.getenv("POSTGRES_SSL", False):
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
    }
    DATABASES["cash_assist_datahub_mis"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=mis",
    }
    DATABASES["cash_assist_datahub_ca"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=ca",
    }
    DATABASES["cash_assist_datahub_erp"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
        "options": "-c search_path=erp",
    }
    DATABASES["registration_datahub"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt",
    }


AIRFLOW_HOST = os.getenv("AIRFLOW_HOST", "hct-mis-airflow-web")

# ELASTICSEARCH SETTINGS
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_HOST, "timeout": 30},
}
