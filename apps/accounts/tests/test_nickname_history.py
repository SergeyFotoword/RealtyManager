import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.accounts.models.profile import UserProfile
from apps.accounts.models.nickname import NicknameHistory

User = get_user_model()


class NicknameHistorySignalTest(TestCase):
    def test_nickname_history_created_on_change(self):

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        profile = UserProfile.objects.create(
            user=user,
            public_id=uuid.uuid4(),
            nickname="old_nick",
        )

        profile.nickname = "new_nick"
        profile.save()

        history = NicknameHistory.objects.get(profile=profile)

        self.assertEqual(history.nickname, "old_nick")

    def test_multiple_nickname_changes_create_multiple_history_records(self):
        user = User.objects.create_user(
            username="multiuser",
            email="multi@example.com",
            password="password123",
        )

        profile = UserProfile.objects.create(
            user=user,
            nickname="nick1",
        )

        profile.nickname = "nick2"
        profile.save()

        profile.nickname = "nick3"
        profile.save()

        history = (
            NicknameHistory.objects
            .filter(profile=profile)
            .order_by("used_at")
        )

        self.assertEqual(history.count(), 2)
        self.assertEqual(history[0].nickname, "nick1")
        self.assertEqual(history[1].nickname, "nick2")

    def test_no_history_created_on_profile_creation(self):
        user = User.objects.create_user(
            username="firstuser",
            email="first@example.com",
            password="password123",
        )

        profile = UserProfile.objects.create(
            user=user,
            nickname="initial_nick",
        )

        self.assertEqual(
            NicknameHistory.objects.filter(profile=profile).count(),
            0
        )