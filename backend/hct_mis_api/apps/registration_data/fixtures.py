import factory
from factory import fuzzy
from pytz import utc

from account.fixtures import UserFactory
from core.models import BusinessArea
from registration_data.models import RegistrationDataImport


class RegistrationDataImportFactory(factory.DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport
        django_get_or_create = ("name",)

    name = factory.Faker("sentence", nb_words=3, variable_nb_words=True, ext_word_list=None,)
    status = "IN_REVIEW"
    import_date = factory.Faker("date_time_this_decade", before_now=True, tzinfo=utc,)
    imported_by = factory.SubFactory(UserFactory)
    data_source = factory.fuzzy.FuzzyChoice(RegistrationDataImport.DATA_SOURCE_CHOICE, getter=lambda c: c[0],)
    number_of_individuals = factory.fuzzy.FuzzyInteger(100, 10000)
    number_of_households = factory.fuzzy.FuzzyInteger(3, 50)
    datahub_id = factory.Faker("uuid4")
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
