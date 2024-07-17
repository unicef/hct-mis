import random
import string
from datetime import timedelta
from random import randint
from typing import Any

from django.utils.timezone import utc

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program, ProgramCycle


class ProgramCycleFactory(DjangoModelFactory):
    class Meta:
        model = ProgramCycle
        django_get_or_create = ("program", "status")

    status = ProgramCycle.ACTIVE
    start_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True,
        ext_word_list=None,
    )
    iteration = factory.Sequence(lambda n: n)


class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ("programme_code", "business_area")

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    name = factory.Faker(
        "sentence",
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    status = fuzzy.FuzzyChoice(
        Program.STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    start_date = factory.Faker(
        "date_this_decade",
        before_today=False,
        after_today=True,
    )
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=randint(60, 1000)))
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True,
        ext_word_list=None,
    )
    budget = factory.fuzzy.FuzzyDecimal(1000000.0, 900000000.0)
    frequency_of_payments = fuzzy.FuzzyChoice(
        Program.FREQUENCY_OF_PAYMENTS_CHOICE,
        getter=lambda c: c[0],
    )
    sector = fuzzy.FuzzyChoice(
        Program.SECTOR_CHOICE,
        getter=lambda c: c[0],
    )
    scope = fuzzy.FuzzyChoice(
        Program.SCOPE_CHOICE,
        getter=lambda c: c[0],
    )
    cash_plus = fuzzy.FuzzyChoice((True, False))
    population_goal = factory.fuzzy.FuzzyDecimal(50000.0, 600000.0)
    administrative_areas_of_implementation = factory.Faker(
        "sentence",
        nb_words=3,
        variable_nb_words=True,
        ext_word_list=None,
    )
    data_collecting_type = factory.SubFactory(DataCollectingTypeFactory)
    programme_code = factory.LazyAttribute(
        lambda o: "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    )

    @factory.post_generation
    def cycle(self, create: bool, extracted: bool, **kwargs: Any) -> None:
        if not create:
            return

        ProgramCycleFactory(program=self, **kwargs)
