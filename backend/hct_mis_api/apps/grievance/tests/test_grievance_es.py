import json
import os
from unittest.mock import patch

from elasticsearch import Elasticsearch
from django.conf import settings

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.documents import CATEGORY_CHOICES, STATUS_CHOICES, PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import GrievanceTicket


def execute_test_es_query(query_dict):
    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search

    es = Elasticsearch("http://elasticsearch:9200")
    es.indices.refresh("test_es_db")
    es_response = (
        Search(using=es, index="test_es_db")
        .params(search_type="dfs_query_then_fetch", preserve_order=True)
        .from_dict(query_dict)
    )
    es_ids = [hit.meta.id for hit in es_response.scan()]
    return es_ids


class TestGrievanceQueryElasticSearch(APITestCase):
    PERMISSION = (
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER
    )

    ALL_GRIEVANCE_QUERY = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at") {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_SEARCH = """
        query AllGrievanceTickets($search: String) {
          allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", search: $search) {
            edges {
              node {
                id
                unicefId
                householdUnicefId
                category
                status
                issueType
                admin
                language
                description
                consent
                createdAt
              }
            }
          }
        }
    """

    FILTER_BY_ADMIN_AREA = """
    query AllGrievanceTickets($admin: [ID]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", admin: $admin) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_CREATED_AT = """
    query AllGrievanceTickets($createdAtRange: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", createdAtRange: $createdAtRange) {
        edges {
          node {
            id
            unicefId
            householdUnicefId
            category
            status
            issueType
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_STATUS = """
    query AllGrievanceTickets($status: [String]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", status: $status) {
        edges {
          node {
            id
            unicefId
            householdUnicefId
            category
            status
            issueType
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    GRIEVANCE_QUERY = """
    query GrievanceTicket($id: ID!) {
      grievanceTicket(id: $id) {
        status
        category
        admin
        language
        description
        consent
        createdAt
      }
    }
    """

    FILTER_BY_CATEGORY = """
    query AllGrievanceTickets($category: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", category: $category) {
        edges {
          node {
            id
            unicefId
            householdUnicefId
            category
            status
            issueType
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_ASSIGNED_TO = """
    query AllGrievanceTickets($assignedTo: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", assignedTo: $assignedTo) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_SCORE = """
    query AllGrievanceTickets($scoreMin: String, $scoreMax: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", scoreMax: $scoreMax, scoreMin: $scoreMin) {
        edges {
          node {
            needsAdjudicationTicketDetails {
              scoreMin
              scoreMax
            }
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        settings.ELASTICSEARCH_GRIEVANCE_TURN_ON = True
        cls.es = cls.create_es_db()

        create_afghanistan()
        cls.user = UserFactory.create()
        cls.user2 = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="123aa123")
        cls.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="sadasdasfd222")

        country = Country.objects.first()
        area_type_new = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
            original_id=area_type.id,
        )
        cls.admin_area_1_new = AreaFactory(
            name="City Test", area_type=area_type_new, p_code="123aa123", original_id=cls.admin_area_1.id
        )
        cls.admin_area_2_new = AreaFactory(
            name="City Example", area_type=area_type_new, p_code="sadasdasfd222", original_id=cls.admin_area_2.id
        )

        cls.grievance_ticket_1 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "admin2": cls.admin_area_1,
                "admin2_new": cls.admin_area_1_new,
                "language": "Polish",
                "consent": True,
                "description": "Just random description",
                "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                "status": GrievanceTicket.STATUS_NEW,
                "created_by": cls.user,
                "assigned_to": cls.user,
                "created_at": "2022-04-30T09:54:07.827000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": 1,
                "urgency": 2
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_1.id,
            body={
                "business_area": cls.grievance_ticket_1.business_area.name.lower(),
                "unicef_id": "GRV-000001",
                "admin": cls.grievance_ticket_1.admin2_new.id,
                "registration_data_import": None,
                "category": CATEGORY_CHOICES.get(cls.grievance_ticket_1.category),
                "status": STATUS_CHOICES.get(cls.grievance_ticket_1.status),
                "issue_type": None,
                "assigned_to": cls.user.id,
                "created_at": "2022-04-30T09:54:07.827000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": PRIORITY_CHOICES.get(cls.grievance_ticket_1.priority),
                "urgency": URGENCY_CHOICES.get(cls.grievance_ticket_1.urgency),
                "grievance_type": "user",
                "head_of_household_last_name": "Kowalska_1",
                "fsp": None
            }
        )

        cls.grievance_ticket_2 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "admin2": cls.admin_area_2,
                "admin2_new": cls.admin_area_2_new,
                "language": "Polish",
                "consent": True,
                "description": "Just random description",
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "status": GrievanceTicket.STATUS_IN_PROGRESS,
                "issue_type": 12,
                "created_by": cls.user2,
                "assigned_to": cls.user2,
                "created_at": "2022-05-12T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0001",
                "priority": 2,
                "urgency": 3
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_2.id,
            body={
                "business_area": cls.grievance_ticket_2.business_area.name.lower(),
                "unicef_id": "GRV-000002",
                "admin": cls.grievance_ticket_2.admin2_new.id,
                "registration_data_import": "04992dce-154b-4938-8e47-74341541ebcf",
                "category": CATEGORY_CHOICES.get(cls.grievance_ticket_2.category),
                "status": STATUS_CHOICES.get(cls.grievance_ticket_2.status),
                "issue_type": "Fraud and forgery",
                "assigned_to": cls.user2.id,
                "created_at": "2022-05-12T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0002",
                "priority": PRIORITY_CHOICES.get(cls.grievance_ticket_2.priority),
                "urgency": URGENCY_CHOICES.get(cls.grievance_ticket_2.urgency),
                "grievance_type": "user",
                "head_of_household_last_name": "Kowalska_2",
                "fsp": "Goldman Sachs"
            }
        )

        cls.grievance_ticket_3 = GrievanceTicket.objects.create(
            **{
                "business_area": cls.business_area,
                "admin2": cls.admin_area_2,
                "admin2_new": cls.admin_area_2_new,
                "language": "Polish",
                "consent": True,
                "description": "Just random description",
                "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                "status": GrievanceTicket.STATUS_ON_HOLD,
                "created_by": cls.user,
                "assigned_to": cls.user,
                "created_at": "2022-05-05T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0003",
                "priority": 3,
                "urgency": 1
            }
        )

        cls.es.index(
            index="test_es_db",
            doc_type="_doc",
            id=cls.grievance_ticket_3.id,
            body={
                "business_area": cls.grievance_ticket_3.business_area.name.lower(),
                "unicef_id": "GRV-000003",
                "admin": cls.grievance_ticket_3.admin2_new.id,
                "registration_data_import": None,
                "category": CATEGORY_CHOICES.get(cls.grievance_ticket_3.category),
                "status": STATUS_CHOICES.get(cls.grievance_ticket_3.status),
                "issue_type": None,
                "assigned_to": cls.user.id,
                "created_at": "2022-05-05T09:12:07.857000",
                "household_unicef_id": "HH-20-0000.0003",
                "priority": PRIORITY_CHOICES.get(cls.grievance_ticket_3.priority),
                "urgency": URGENCY_CHOICES.get(cls.grievance_ticket_3.urgency),
                "grievance_type": "user",
                "head_of_household_last_name": "Kowalska_3",
                "fsp": None
            }
        )

    @staticmethod
    def create_es_db():
        grievance_es_index = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "tests", "grievance_es_index.json"
        )

        with open(grievance_es_index) as f:
            es = Elasticsearch("http://elasticsearch:9200")
            es.indices.create(
                index="test_es_db",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "index.store.type": "mmapfs",
                    },
                    "mappings": json.load(f)
                }
            )

        return es

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_unicef_id(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": "ticket_id GRV-000001"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_household_unicef_id(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": "ticket_hh_id HH-20-0000.0003"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_head_of_household_last_name(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SEARCH,
            context={"user": self.user},
            variables={"search": "last_name Kowalska_1"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_category(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CATEGORY,
            context={"user": self.user},
            variables={"category": "Positive Feedback"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_status(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={"user": self.user},
            variables={"status": ["On Hold"]},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_min_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"created_at": '{"max": "2022-05-01"}'},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_max_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"created_at": '{"min": "2022-05-10"}'},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_min_and_max_date_range(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"created_at": '{"min": "2022-05-01", "max": "2022-05-10"}'},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_admin(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"admin": self.grievance_ticket_1.admin2_new.id},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_admin(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"admin": self.grievance_ticket_1.admin2_new.id},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_issue_type(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"issue_type": "Fraud and forgery"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_priority(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"priority": "Low"},
        )

    @patch("hct_mis_api.apps.grievance.schema.execute_es_query", side_effect=execute_test_es_query)
    def test_grievance_query_es_search_by_urgency(self, mock_execute_test_es_query):
        self.create_user_role_with_permissions(self.user, [*self.PERMISSION], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={"user": self.user},
            variables={"urgency": "Very urgent"},
        )