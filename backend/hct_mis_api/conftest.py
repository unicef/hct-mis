import logging
import os
import sys

from django.conf import settings

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import connections


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--localhost",
        action="store_true",
        default=False,
        help="Tests running locally, no ES",
    )


def pytest_configure(config: Config) -> None:
    pytest.localhost = True if config.getoption("--localhost") else False

    sys._called_from_pytest = True
    from django.conf import settings

    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]
    settings.CELERY_TASK_ALWAYS_EAGER = True

    settings.ELASTICSEARCH_INDEX_PREFIX = "test_"
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    settings.CATCH_ALL_EMAIL = []
    settings.DEFAULT_EMAIL = "testemail@email.com"

    settings.EXCHANGE_RATE_CACHE_EXPIRY = 0
    settings.USE_DUMMY_EXCHANGE_RATES = True

    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
    settings.CSRF_COOKIE_SECURE = False
    settings.CSRF_COOKIE_HTTPONLY = False
    settings.SESSION_COOKIE_SECURE = False
    settings.SESSION_COOKIE_HTTPONLY = True
    settings.SECURE_HSTS_SECONDS = False
    settings.SECURE_CONTENT_TYPE_NOSNIFF = True
    settings.SECURE_REFERRER_POLICY = "same-origin"

    settings.CACHE_ENABLED = False
    settings.CACHES = {
        "default": {
            "BACKEND": "hct_mis_api.apps.core.memcache.LocMemCache",
            "TIMEOUT": 1800,
        }
    }

    settings.LOGGING["loggers"].update(
        {
            "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
            "registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "sanction_list.tasks.check_against_sanction_list_pre_merge": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "graphql": {"handlers": ["default"], "level": "CRITICAL", "propagate": True},
            "elasticsearch": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "elasticsearch-dsl-django": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hct_mis_api.apps.registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
        }
    )

    logging.disable(logging.CRITICAL)


def pytest_unconfigure(config: Config) -> None:
    import sys

    del sys._called_from_pytest


disabled_locally_test = pytest.mark.skip(
    reason="Elasticsearch error - to investigate",
)


@pytest.fixture(scope="session")
def django_elasticsearch_setup(request: pytest.FixtureRequest) -> None:
    xdist_suffix = getattr(request.config, "workerinput", {}).get("workerid")
    if xdist_suffix:  # pragma: no cover
        # Put a suffix like _gw0, _gw1 etc on xdist processes
        _set_suffix_to_test_elasticsearch(suffix=xdist_suffix)


def _set_suffix_to_test_elasticsearch(suffix: str) -> None:
    worker_connection_postfix = f"default_worker_{suffix}"
    connections.create_connection(alias=worker_connection_postfix, **settings.ELASTICSEARCH_DSL["default"])

    # Update index names and connections
    for doc in registry.get_documents():
        doc._index._name += f"_{suffix}"
        # Use the worker-specific connection
        doc._index._using = worker_connection_postfix
