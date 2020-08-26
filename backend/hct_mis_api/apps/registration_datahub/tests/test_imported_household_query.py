from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from registration_datahub.fixtures import ImportedHouseholdFactory


class TestImportedHouseholdQuery(APITestCase):
    multi_db = True

    ALL_IMPORTED_HOUSEHOLD_QUERY = """
    query AllImportedHouseholds{
      allImportedHouseholds {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """
    IMPORTED_HOUSEHOLD_QUERY = """
    query ImportedHousehold($id: ID!) {
      importedHousehold(id: $id) {
        size
        countryOrigin
        address
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        sizes_list = (2, 4, 5, 1, 3, 11, 14)
        self.households = [
            ImportedHouseholdFactory(size=size, address="Lorem Ipsum", country_origin="PL",) for size in sizes_list
        ]

    def test_imported_household_query_all(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_HOUSEHOLD_QUERY, context={"user": self.user},
        )

    def test_imported_household_query_single(self):
        self.snapshot_graphql_request(
            request_string=self.IMPORTED_HOUSEHOLD_QUERY,
            context={"user": self.user},
            variables={"id": self.id_to_base64(self.households[0].id, "ImportedHousehold")},
        )
