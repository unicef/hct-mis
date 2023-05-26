from django.test import TestCase, override_settings

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.power_query.celery_tasks import run_background_query
from hct_mis_api.apps.power_query.defaults import create_defaults
from hct_mis_api.apps.power_query.models import Formatter, Parametrizer, Query, Report
from hct_mis_api.apps.power_query.tests.fixtures import FormatterFactory, ParametrizerFactory, QueryFactory, ReportFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryCelery(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()

        cls.params: Parametrizer = ParametrizerFactory()
        cls.query1: Query = QueryFactory(code="result=conn.all()")
        cls.query2: Query = QueryFactory(code=f"result=invoke({cls.query1.pk}, arguments)")
        cls.formatter: Formatter = FormatterFactory(name="Queryset To HTML")
        cls.report: Report = ReportFactory(formatter=cls.formatter, query=cls.query1)

    def test_query_queue(self) -> None:
        run_background_query.delay(self.query1.pk)
        assert self.query1.datasets.exists()
