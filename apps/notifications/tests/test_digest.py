from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.notifications.models import NotificationLog, NotificationPreference
from apps.notifications.services.digest import DigestService

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_with_digest_enabled(user_factory):
    user = user_factory(email="digest_user@example.com", is_active=True)
    NotificationPreference.objects.create(
        user=user,
        instant_emails=True,
        daily_digest=True,
        last_digest_sent_at=None,
    )
    return user


@pytest.fixture
def user_with_digest_disabled(user_factory):
    user = user_factory(email="no_digest@example.com", is_active=True)
    NotificationPreference.objects.create(
        user=user,
        instant_emails=True,
        daily_digest=False,
        last_digest_sent_at=None,
    )
    return user


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_digest_sends_once_per_24h(mock_send, user_with_digest_enabled):
    # Create a notification log within the last 24h
    NotificationLog.objects.create(
        recipient=user_with_digest_enabled,
        event_type="booking",
        subject="New booking request",
        template="booking/pending_created",
        context={"booking_id": 1},
        success=True,
        error="",
    )

    DigestService.send_daily_digest(user_with_digest_enabled)
    DigestService.send_daily_digest(user_with_digest_enabled)  # should not send again

    assert mock_send.call_count == 1

    prefs = user_with_digest_enabled.notification_preferences
    assert prefs.last_digest_sent_at is not None


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_digest_does_nothing_if_disabled(mock_send, user_with_digest_disabled):
    NotificationLog.objects.create(
        recipient=user_with_digest_disabled,
        event_type="booking",
        subject="New booking request",
        template="booking/pending_created",
        context={"booking_id": 1},
        success=True,
        error="",
    )

    DigestService.send_daily_digest(user_with_digest_disabled)

    assert mock_send.call_count == 0


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_digest_respects_rolling_24h_window(mock_send, user_with_digest_enabled):
    # Two logs: one old, one recent → digest should include at least recent and still send once
    old_time = timezone.now() - timedelta(days=2)

    # Create older log by overriding sent_at in DB (works if model allows update)
    old_log = NotificationLog.objects.create(
        recipient=user_with_digest_enabled,
        event_type="booking",
        subject="Old event",
        template="booking/confirmed",
        context={"booking_id": 99},
        success=True,
        error="",
    )
    NotificationLog.objects.filter(id=old_log.id).update(sent_at=old_time)

    NotificationLog.objects.create(
        recipient=user_with_digest_enabled,
        event_type="booking",
        subject="Recent event",
        template="booking/pending_created",
        context={"booking_id": 100},
        success=True,
        error="",
    )

    DigestService.send_daily_digest(user_with_digest_enabled)

    assert mock_send.call_count == 1