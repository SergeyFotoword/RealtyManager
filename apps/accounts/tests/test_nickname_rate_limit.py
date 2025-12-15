from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.accounts.models.profile import UserProfile
from apps.accounts.services.profile import change_nickname

User = get_user_model()


class NicknameRateLimitTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="ratelimit",
            email="rate@example.com",
            password="pass",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            nickname="FirstNick",
        )

    def test_cannot_change_nickname_twice_within_30_days(self):
        change_nickname(self.profile, "SecondNick")

        with self.assertRaises(ValidationError):
            change_nickname(self.profile, "ThirdNick")

    def test_can_change_nickname_after_30_days(self):
        change_nickname(self.profile, "SecondNick")

        # roll back time
        self.profile.nickname_updated_at = timezone.now() - timedelta(days=31)
        self.profile.save(update_fields=["nickname_updated_at"])

        change_nickname(self.profile, "ThirdNick")