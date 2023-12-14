from typing import Any, List
from unittest.mock import patch

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

FILTER_GRIEVANCE_BY_CROSS_AREA = """
query AllGrievanceTickets($isCrossArea: Boolean) {
  allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", isCrossArea: $isCrossArea) {
    edges {
      node {
        status
        category
        admin
        language
        description
        consent
      }
    }
  }
}
"""


@patch("hct_mis_api.apps.core.es_filters.ElasticSearchFilterSet.USE_ALL_FIELDS_AS_POSTGRES_DB", True)
class TestCrossAreaFilterAvailable(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(partner=partner_unicef)

        cls.admin_area1 = AreaFactory(name="Admin Area 1", level=2)
        cls.admin_area2 = AreaFactory(name="Admin Area 2", level=2)
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)

        individual1_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        individual2_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        household1_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area1, head_of_household=individual1_from_area1
        )
        individual1_from_area1.household = household1_from_area1
        individual1_from_area1.save()
        household2_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area1, head_of_household=individual2_from_area1
        )
        individual2_from_area1.household = household2_from_area1
        individual2_from_area1.save()

        individual_from_area2 = IndividualFactory(business_area=cls.business_area, household=None)
        household_from_area2 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area2, head_of_household=individual_from_area2
        )
        individual_from_area2.household = household_from_area2
        individual_from_area2.save()

        grievance_ticket_cross_area = GrievanceTicketFactory(
            business_area=cls.business_area,
            language="Polish",
            consent=True,
            description="Cross Area Grievance",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            assigned_to=cls.user,
            admin2=cls.admin_area2,
        )
        grievance_ticket_cross_area.programs.set([cls.program])
        cls.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=grievance_ticket_cross_area,
        )
        cls.needs_adjudication_ticket_cross_area.possible_duplicates.set([individual_from_area2])
        cls.needs_adjudication_ticket_cross_area.populate_cross_area_flag()

        grievance_ticket_same_area = GrievanceTicketFactory(
            business_area=cls.business_area,
            language="Polish",
            consent=True,
            description="Same Area Grievance",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            assigned_to=cls.user,
            admin2=cls.admin_area2,
        )
        grievance_ticket_same_area.programs.set([cls.program])
        cls.needs_adjudication_ticket_same_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=grievance_ticket_same_area,
        )
        cls.needs_adjudication_ticket_same_area.possible_duplicates.set([individual2_from_area1])
        cls.needs_adjudication_ticket_same_area.populate_cross_area_flag()

        # testing different access requirements
        cls.partner_without_area_restrictions = PartnerFactory(name="Partner without area restrictions")
        cls.partner_without_area_restrictions.permissions = {
            str(cls.business_area.id): {"programs": {str(cls.program.id): []}}
        }
        cls.partner_with_area_restrictions = PartnerFactory(name="Partner with area restrictions")
        cls.partner_with_area_restrictions.permissions = {
            str(cls.business_area.id): {
                "programs": {str(cls.program.id): [str(cls.admin_area1.id), str(cls.admin_area2.id)]}
            }
        }

    @parameterized.expand(
        [
            (
                "without_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            ),
            (
                "with_permission",
                [
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_CROSS_AREA_FILTER,
                ],
            ),
        ]
    )
    def test1_cross_area_filter_true_full_area_access(self, _: Any, permissions: List[Permissions]) -> None:
        user_without_permission = UserFactory(partner=self.partner_without_area_restrictions)
        self.create_user_role_with_permissions(
            user_without_permission,
            permissions,
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": user_without_permission,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )

    def test_cross_area_filter_true(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.needs_adjudication_ticket_cross_area.refresh_from_db()
        self.needs_adjudication_ticket_same_area.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_cross_area.is_cross_area, True)
        self.assertEqual(self.needs_adjudication_ticket_same_area.is_cross_area, False)

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )

    def test_without_cross_area_filter(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": None},
        )

    def test_cross_area_filter_true_but_area_restrictions(self) -> None:
        user_with_area_restrictions = UserFactory(partner=self.partner_with_area_restrictions)
        self.create_user_role_with_permissions(
            user_with_area_restrictions,
            [
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_CROSS_AREA_FILTER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": user_with_area_restrictions,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )