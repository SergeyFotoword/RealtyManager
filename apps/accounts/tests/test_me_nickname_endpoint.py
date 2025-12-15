from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models.profile import UserProfile

User = get_user_model()


class MeNicknameEndpointTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="meuser",
            email="me@example.com",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            nickname="StartNick",
        )
        self.url = reverse("me-nickname")

    def test_get_requires_auth(self):
        resp = self.client.get(self.url)
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_get_returns_current_nickname_and_timestamp(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["nickname"], "StartNick")
        # The field may be null if you haven't changed your nickname through the service yet.
        self.assertIn("nickname_updated_at", resp.data)

    def test_patch_changes_nickname_and_sets_updated_at(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.url, {"nickname": "NewNick"}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["nickname"], "NewNick")
        self.assertIsNotNone(resp.data["nickname_updated_at"])

    def test_patch_rate_limit_blocks_second_change(self):
        self.client.force_authenticate(user=self.user)

        # 1st nickname change - ok
        r1 = self.client.patch(self.url, {"nickname": "Nick1"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # 2nd nickname change immediately - should be blocked (400)
        r2 = self.client.patch(self.url, {"nickname": "Nick2"}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", r2.data)

    def test_patch_allows_change_after_cooldown(self):
        self.client.force_authenticate(user=self.user)

        # Change nickname once
        r1 = self.client.patch(self.url, {"nickname": "Nick1"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # "Rewinding time" beyond Cooldown
        self.profile.refresh_from_db()
        self.profile.nickname_updated_at = timezone.now() - timedelta(days=31)
        self.profile.save(update_fields=["nickname_updated_at"])

        # now you can again
        r2 = self.client.patch(self.url, {"nickname": "Nick2"}, format="json")
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.data["nickname"], "Nick2")

    def test_optimistic_locking_returns_409_when_stale(self):
        """
        Only works if the endpoint supports expected_nickname_updated_at.
        """
        self.client.force_authenticate(user=self.user)

        # Let's take the current state
        g = self.client.get(self.url)
        self.assertEqual(g.status_code, status.HTTP_200_OK)
        expected = g.data["nickname_updated_at"]

        # Change your nickname (updated_at will change)
        r1 = self.client.patch(self.url, {"nickname": "Nick1"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        # We are trying to change it again, but with an outdated expected value.
        r2 = self.client.patch(
            self.url,
            {"nickname": "Nick2", "expected_nickname_updated_at": expected},
            format="json",
        )
        self.assertEqual(r2.status_code, status.HTTP_409_CONFLICT)