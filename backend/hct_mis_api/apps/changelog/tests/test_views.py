from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from hct_mis_api.apps.core.base_test_case import TimeMeasuringTestCase
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.changelog.factory import ChangelogFactory

User = get_user_model()


class APITestCase(TestCase, TimeMeasuringTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.user = UserFactory()

    def tests_changelog_list_view(self) -> None:
        instance1 = ChangelogFactory(active=True)
        instance2 = ChangelogFactory(active=True)
        url = reverse("changelog_changelog_list")
        # Log out
        self.client.logout()
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND, msg="You need to be logged in")
        self.client.force_login(self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "You need to be logged in and superuser")
        self.assertIn(str(instance1.version), resp.content.decode("utf-8"))
        self.assertIn(str(instance2.date), resp.content.decode("utf-8"))

    def tests_changelog_detail_view(self) -> None:
        instance = ChangelogFactory()
        url = reverse(
            "changelog_changelog_detail",
            args=[
                instance.pk,
            ],
        )
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, "You need to be logged in and superuser")
        self.assertIn(str(instance.version), response.content.decode("utf-8"))
