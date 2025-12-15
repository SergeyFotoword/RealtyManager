from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.accounts.models.profile import UserProfile
from apps.accounts.models.nickname import NicknameHistory
from apps.accounts.services.nickname import is_nickname_available
from django.core.exceptions import ValidationError
from apps.accounts.services.profile import change_nickname

User = get_user_model()


class NicknameAvailabilityTest(TestCase):

    def test_nickname_available_when_unused(self):
        self.assertTrue(is_nickname_available("FreshNick"))

    def test_nickname_unavailable_if_used_by_profile(self):
        user = User.objects.create_user(
            username="u1",
            email="u1@example.com",
            password="pass",
        )

        UserProfile.objects.create(
            user=user,
            nickname="TakenNick",
        )

        self.assertFalse(is_nickname_available("TakenNick"))

    def test_nickname_unavailable_if_used_in_history(self):
        user = User.objects.create_user(
            username="u2",
            email="u2@example.com",
            password="pass",
        )

        profile = UserProfile.objects.create(
            user=user,
            nickname="CurrentNick",
        )

        NicknameHistory.objects.create(
            profile=profile,
            nickname="OldNick",
        )

        self.assertFalse(is_nickname_available("OldNick"))

    def test_cannot_reuse_old_nickname_of_another_user(self):
        user1 = User.objects.create_user(
            username="u1",
            email="u1@example.com",
            password="pass",
        )
        profile1 = UserProfile.objects.create(
            user=user1,
            nickname="Vasia",
        )

        profile1.nickname = "Vasia123"
        profile1.save()

        user2 = User.objects.create_user(
            username="u2",
            email="u2@example.com",
            password="pass",
        )
        profile2 = UserProfile.objects.create(
            user=user2,
            nickname="Ira",
        )

        with self.assertRaises(ValidationError):
            change_nickname(profile2, "Vasia")