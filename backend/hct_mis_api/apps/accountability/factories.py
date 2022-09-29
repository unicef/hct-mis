import random

import factory

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.models import FeedbackMessage, Feedback
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Area


class FeedbackFactory(factory.DjangoModelFactory):
    class Meta:
        model = Feedback

    created_by = factory.SubFactory(UserFactory)
    issue_type = factory.fuzzy.FuzzyChoice(
        (
            Feedback.POSITIVE_FEEDBACK,
            Feedback.NEGATIVE_FEEDBACK,
        )
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    admin2 = factory.LazyAttribute(
        lambda o: Area.objects.filter(area_type__country__name__iexact="afghanistan").first()
    )
    area = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    language = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())


class FeedbackMessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = FeedbackMessage

    feedback = factory.SubFactory(
        FeedbackFactory,
        issue_type=random.choice(
            (
                Feedback.POSITIVE_FEEDBACK,
                Feedback.NEGATIVE_FEEDBACK,
            )
        ),
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    created_by = factory.SubFactory(UserFactory)
