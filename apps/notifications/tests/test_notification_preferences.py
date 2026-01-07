from unittest.mock import patch

import pytest

from apps.notifications.models import NotificationLog, NotificationPreference
from apps.notifications.services.base import NotificationService

pytestmark = pytest.mark.django_db


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_instant_emails_disabled_does_not_send_but_logs(mock_send, user_factory):
    user = user_factory(email="prefs@example.com", is_active=True)

    NotificationPreference.objects.create(
        user=user,
        instant_emails=False,
        daily_digest=True,
    )

    NotificationService.send_email(
        to_user=user,
        subject="Test subject",
        template="booking/pending_created",
        context={"booking_id": 123},
        event_type="booking",
    )

    assert mock_send.call_count == 0

    log = NotificationLog.objects.filter(
        recipient=user,
        template="booking/pending_created",
        event_type="booking",
    ).first()

    assert log is not None
    assert log.success is True
    assert "Instant emails disabled" in (log.error or "")


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_missing_email_logs_failure_and_does_not_send(mock_send, user_factory):
    user = user_factory(email="", is_active=True)

    NotificationService.send_email(
        to_user=user,
        subject="Test subject",
        template="booking/pending_created",
        context={"booking_id": 123},
        event_type="booking",
    )

    assert mock_send.call_count == 0

    log = NotificationLog.objects.filter(
        recipient=user,
        template="booking/pending_created",
        event_type="booking",
        success=False,
    ).first()

    assert log is not None
    assert "has no email" in (log.error or "")