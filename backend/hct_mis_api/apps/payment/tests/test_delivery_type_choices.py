from account.fixtures import UserFactory
from core.tests import APITestCase


class TestDeliveryTypeChoices(APITestCase):
    QUERY_DELIVERY_TYPE_CHOICES = """
    query DeliveryTypeChoices {
        paymentDeliveryTypeChoices
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()

    def test_delivery_type_choices_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_DELIVERY_TYPE_CHOICES,
            context={'user': self.user}
        )