from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.accounts.models.profile import UserProfile
from apps.accounts.models.nickname import NicknameHistory

User = get_user_model()


class ProfileNicknameRedirectsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u_nick",
            email="u_nick@example.com",
            password="password123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            nickname="Vasia",
        )

    def test_current_nickname_redirects_to_public_id(self):
        """
        /@Vasia -> 302 -> /users/<public_id>/
        """
        url = reverse("profile_by_nickname", kwargs={"nickname": "Vasia"})
        resp = self.client.get(url, follow=False)

        self.assertEqual(resp.status_code, 302)

        expected = reverse(
            "profile_by_public_id",
            kwargs={"public_id": self.profile.public_id},
        )
        self.assertEqual(resp["Location"], expected)

    def test_old_nickname_redirects_to_current_nickname_permanently(self):
        """
        /@Vasia (old) -> 301 -> /@Vasia123 (current)
        """
        # change the nickname (the signal should record the old nickname in NicknameHistory)
        self.profile.nickname = "Vasia123"
        self.profile.save()

        # sanity-check: the story really happened
        self.assertTrue(
            NicknameHistory.objects.filter(
                profile=self.profile,
                nickname__iexact="Vasia",
            ).exists()
        )

        old_url = reverse("profile_by_nickname", kwargs={"nickname": "Vasia"})
        resp = self.client.get(old_url, follow=False)

        self.assertEqual(resp.status_code, 301)

        new_url = reverse("profile_by_nickname", kwargs={"nickname": "Vasia123"})
        self.assertEqual(resp["Location"], new_url)

    def test_unknown_nickname_returns_404(self):
        url = reverse("profile_by_nickname", kwargs={"nickname": "NoSuchNick"})
        resp = self.client.get(url, follow=False)
        self.assertEqual(resp.status_code, 404)

    def test_nickname_lookup_is_case_insensitive(self):
        url = reverse("profile_by_nickname", kwargs={"nickname": "vasia"})
        resp = self.client.get(url, follow=False)
        self.assertEqual(resp.status_code, 302)