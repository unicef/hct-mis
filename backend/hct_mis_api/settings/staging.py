from __future__ import absolute_import
from .base import *  # noqa: ignore=F403


# dev overrides
DEBUG = False
IS_STAGING = True

# domains/hosts etc.
DOMAIN_NAME = "dev-hct.unitst.org"
WWW_ROOT = "https://%s/" % DOMAIN_NAME
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "*",
    "10.0.2.2",
    os.getenv("DOMAIN", ""),
]

# other
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 1800,
    }
}

## STORAGE
STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"

AZURE_ACCOUNT_NAME = os.getenv("STORAGE_AZURE_ACCOUNT_NAME", "")
AZURE_ACCOUNT_KEY = os.getenv("STORAGE_AZURE_ACCOUNT_KEY", "")

AZURE_CUSTOM_DOMAIN = f"{AZURE_ACCOUNT_NAME}.blob.core.windows.net"
STATIC_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{STATIC_LOCATION}/"
MEDIA_URL = f"https://{AZURE_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/"

DEFAULT_FILE_STORAGE = "core.storage.AzureMediaStorage"
STATICFILES_STORAGE = "core.storage.AzureStaticStorage"
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

if os.getenv("POSTGRES_SSL", False):
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "verify-full",
        "sslrootcert": "/code/psql-cert.crt"
    }

DATABASES["cash_assist_datahub"] = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_CASHASSIST_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_CASHASSIST_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_CASHASSIST_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_CASHASSIST_DATAHUB_HOST"),
        "PORT": 5432,
}

DATABASES["registration_datahub"] = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_REGISTRATION_DATAHUB_DB"),
        "USER": os.getenv("POSTGRES_REGISTRATION_DATAHUB_USER"),
        "PASSWORD": os.getenv("POSTGRES_REGISTRATION_DATAHUB_PASSWORD"),
        "HOST": os.getenv("POSTGRES_REGISTRATION_DATAHUB_HOST"),
        "PORT": 5432,
}
