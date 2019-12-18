from __future__ import absolute_import

import os
import sys

####
# Change per project
####
from django.utils.text import slugify

PROJECT_NAME = 'hct_mis_api'
# project root and add "apps" to the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, 'apps/'))

# domains/hosts etc.
DOMAIN_NAME = os.getenv('DJANGO_ALLOWED_HOST', 'localhost')
WWW_ROOT = 'http://%s/' % DOMAIN_NAME
ALLOWED_HOSTS = [DOMAIN_NAME]
FRONTEND_HOST = os.getenv('HCT_MIS_FRONTEND_HOST', DOMAIN_NAME)

####
# Other settings
####
ADMINS = (
    ('Alerts', os.getenv('ALERTS_EMAIL') or 'admin@hct-mis.com'),
    ('Tivix', f'unicef-hct-mis+{slugify(DOMAIN_NAME)}@tivix.com'),
)

SITE_ID = 1
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
SECRET_KEY = os.getenv('SECRET_KEY')
DEFAULT_CHARSET = 'utf-8'
ROOT_URLCONF = 'hct_mis_api.urls'

DATA_VOLUME = os.getenv('DATA_VOLUME', '/data')

ALLOWED_EXTENSIONS = (
    'pdf', 'doc', 'docx', 'xls', 'xlsx' 'img', 'png', 'jpg', 'jpeg', 'csv', 'zip'
)
UPLOADS_DIR_NAME = 'uploads'
MEDIA_URL = f'/api/{UPLOADS_DIR_NAME}/'
MEDIA_ROOT = os.getenv('HCT_MIS_UPLOADS_PATH', os.path.join(DATA_VOLUME, UPLOADS_DIR_NAME))

FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024  # 25mb
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

# static resources related. See documentation at: http://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/
STATIC_URL = '/api/static/'
STATIC_ROOT = f'{DATA_VOLUME}/staticserve'

# static serving
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder'
)

DEBUG = True
IS_DEV = False
IS_STAGING = False
IS_PROD = False

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'HCT-MIS Stage <noreply@hct-mis.org>')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', '').lower() == 'true'

# Get the ENV setting. Needs to be set in .bashrc or similar.
ENV = os.getenv('ENV')
if not ENV:
    raise Exception('Environment variable ENV is required!')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': 5432,
    },
    'cash_assist_datahub': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_CASHASSIST_DATAHUB_DB'),
        'USER': os.getenv('POSTGRES_CASHASSIST_DATAHUB_USER'),
        'PASSWORD': os.getenv('POSTGRES_CASHASSIST_DATAHUB_PASSWORD'),
        'HOST': os.getenv('POSTGRES_CASHASSIST_DATAHUB_HOST'),
        'PORT': 5432,
    },
    'registration_datahub': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_REGISTRATION_DATAHUB_DB'),
        'USER': os.getenv('POSTGRES_REGISTRATION_DATAHUB_USER'),
        'PASSWORD': os.getenv('POSTGRES_REGISTRATION_DATAHUB_PASSWORD'),
        'HOST': os.getenv('POSTGRES_REGISTRATION_DATAHUB_HOST'),
        'PORT': 5432,
    },

}

# If app is not specified here it will use default db
DATABASE_APPS_MAPPING = {
    'cash_assist_datahub': 'cash_assist_datahub',
    'registration_datahub': 'registration_datahub',
}

DATABASE_ROUTERS = ('core.dbrouters.DbRouter',)

POSTGRES_SSL_MODE = os.getenv('POSTGRES_SSL_MODE', 'off')
if POSTGRES_SSL_MODE == 'on':
    DATABASES['default'].update({'OPTIONS': {"sslmode": 'require'}})

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                # Social auth context_processors
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]
PROJECT_APPS = [
    'account',
    'core',
    'grievance',
    'household',
    'id_management',
    'intervention',
    'payment',
    'program',
    'targeting',
    'utils',
    'cash_assist_datahub',
    'registration_datahub',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
]

OTHER_APPS = [
    'django_countries',
    'phonenumber_field',
    'compressor',
    'graphene_django',
    'social_django',
]

INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + PROJECT_APPS

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

PASSWORD_RESET_TIMEOUT_DAYS = 31

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.azuread_tenant.AzureADTenantOAuth2',
]

TEST_RUNNER = os.getenv('DJANGO_TEST_RUNNER', 'django.test.runner.DiscoverRunner')
NOSE_ARGS = ['--with-timer', '--nocapture', '--nologcapture']


# helper function to extend all the common lists
def extend_list_avoid_repeats(list_to_extend, extend_with):
    """Extends the first list with the elements in the second one, making sure its elements are not already there in the
    original list."""
    list_to_extend.extend(filter(lambda x: not list_to_extend.count(x), extend_with))


LOG_LEVEL = 'DEBUG' if DEBUG and 'test' not in sys.argv else 'INFO'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s line %(lineno)d: %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s][%(levelname)s][%(name)s] %(filename)s.%(funcName)s:%(lineno)d %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'console': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['mail_admins', 'default'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            # Skip "SuspiciousOperation: Invalid HTTP_HOST" e-mails.
            'handlers': ['default'],
            'propagate': False,
        },
    }
}

GIT_VERSION = os.getenv('GIT_VERSION', 'UNKNOWN')

REDIS_INSTANCE = os.getenv('REDIS_INSTANCE')

if REDIS_INSTANCE:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://{REDIS_INSTANCE}/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'TIMEOUT': 3600
        }
    }
    DJANGO_REDIS_IGNORE_EXCEPTIONS = not DEBUG
else:
    CACHES = {
        'default': {
            'BACKEND': 'common.cache_backends.DummyRedisCache',
            'LOCATION': 'hct_mis'
        }
    }

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
AUTH_USER_MODEL = 'account.User'

GRAPHENE = {
    'SCHEMA': 'hct_mis_api.schema.schema',
    'SCHEMA_OUTPUT': 'schema.json',
    'SCHEMA_INDENT': 2
}

# Social Auth settings.
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY = os.environ.get('AZURE_CLIENT_ID')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = os.environ.get('AZURE_TENANT_KEY')
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email']
SOCIAL_AUTH_POSTGRES_JSONFIELD = True

SOCIAL_AUTH_PIPELINE = (
    # 'account.authentication.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    # 'account.authentication.require_email',
    'social_core.pipeline.social_auth.associate_by_email',
    # 'account.authentication.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    # 'account.authentication.user_details',
)
SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_USER_FIELDS = [
    'email', 'fullname',
]

SOCIAL_AUTH_AZUREAD_B2C_OAUTH2_SCOPE = [
    'openid', 'email', 'profile',
]

SOCIAL_AUTH_SANITIZE_REDIRECTS = True
