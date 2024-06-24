import pytest
from helpers.fixtures import get_program_with_dct_type_and_name
from page_object.accountability.communication import AccountabilityCommunication
from page_object.accountability.comunication_details import (
    AccountabilityCommunicationDetails,
)

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.accountability.fixtures import CommunicationMessageFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation

from page_object.accountability.surveys import AccountabilitySurveys
from page_object.accountability.surveys_details import AccountabilitySurveysDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_accountability_surveys_message() -> None:
    pass


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_accountability_surveys(
        self,
        test_program: Program,
        add_accountability_surveys_message: Message,
        pageAccountabilitySurveys: AccountabilitySurveys,
    ) -> None:
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()

    def test_smoke_accountability_surveys_details(
        self,
        test_program: Program,
        add_accountability_surveys_message: Message,
        pageAccountabilitySurveys: AccountabilitySurveys,
        pageAccountabilitySurveysDetails: AccountabilitySurveysDetails,
    ) -> None:
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()
        pageAccountabilitySurveys.getRows()[0].click()
