import random

import factory
from factory import fuzzy
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea, AdminArea
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketSensitiveDetails,
    TicketComplaintDetails,
    TicketNote,
    TicketAddIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketHouseholdDataUpdateDetails,
    TicketDeleteIndividualDetails,
    TicketSystemFlaggingDetails,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory


class GrievanceTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = GrievanceTicket

    user_modified = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)
    created_by = factory.SubFactory(UserFactory)
    assigned_to = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice(GrievanceTicket.STATUS_CHOICES, getter=lambda c: c[0])
    category = factory.fuzzy.FuzzyChoice(
        (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_REFERRAL,
        )
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    admin = factory.LazyAttribute(
        lambda o: AdminArea.objects.filter(admin_area_level__business_area__slug="afghanistan")
    )
    area = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    language = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    created_at = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)


class SensitiveGrievanceTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSensitiveDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None

    @factory.post_generation
    def create_extras(obj, create, extracted, **kwargs):
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_record = PaymentRecordFactory(household=household)
        obj.save()


class GrievanceComplaintTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT)
    household = None
    individual = None
    payment_record = None

    @factory.post_generation
    def create_extras(obj, create, extracted, **kwargs):
        household, individuals = create_household(
            household_args={"size": 2, "business_area": obj.ticket.business_area},
        )
        obj.household = household
        obj.individual = individuals[0]
        obj.payment_record = PaymentRecordFactory(household=household)

        obj.save()


class SensitiveGrievanceTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSensitiveDetails

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        issue_type=random.choice(
            list(GrievanceTicket.ISSUE_TYPES_CHOICES[GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE].keys())
        ),
    )
    household = None
    individual = None
    payment_record = None


class GrievanceComplaintTicketWithoutExtrasFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketComplaintDetails

    ticket = factory.SubFactory(GrievanceTicketFactory, category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT)
    household = None
    individual = None
    payment_record = None


class TicketNoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketNote

    ticket = factory.SubFactory(
        GrievanceTicketFactory,
        category=random.choice(
            (
                GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                GrievanceTicket.CATEGORY_REFERRAL,
            )
        ),
    )
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    created_by = factory.SubFactory(UserFactory)


class TicketAddIndividualDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketAddIndividualDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    household = None
    individual_data = {}
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketDeleteIndividualDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketDeleteIndividualDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        ),
    )
    individual = None
    approve_status = factory.fuzzy.FuzzyChoice([True, False])


class TicketIndividualDataUpdateDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketIndividualDataUpdateDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    individual = None
    individual_data = {}


class TicketHouseholdDataUpdateDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketHouseholdDataUpdateDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        ),
    )
    household = None
    household_data = {}


class TicketSystemFlaggingDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketSystemFlaggingDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            issue_type=None,
        ),
    )


class TicketNeedsAdjudicationDetailsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TicketNeedsAdjudicationDetails

    ticket = (
        factory.SubFactory(
            GrievanceTicketFactory,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            issue_type=None,
        ),
    )
