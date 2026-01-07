from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.notifications.enums import NotificationEventType
from apps.notifications.models import NotificationLog
from apps.notifications.services.review_notifications import ReviewNotificationService

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff_moderator(db):
    return User.objects.create_user(
        username="moderator",
        email="moderator@test.com",
        password="password123",
        is_staff=True,
        is_active=True,
    )


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_new_review_notifies_target_user(mock_send, review):
    mock_send.return_value = 1

    ReviewNotificationService.new_review_for_user(review)

    assert NotificationLog.objects.filter(
        recipient=review.target,
        event_type=NotificationEventType.REVIEW,
        template="reviews/new_review_user",
        success=True,
    ).exists()

    assert mock_send.called


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_new_review_notifies_moderators(mock_send, review, staff_moderator):
    mock_send.return_value = 1

    ReviewNotificationService.new_review_for_moderators(review)

    assert NotificationLog.objects.filter(
        recipient=staff_moderator,
        event_type=NotificationEventType.REVIEW,
        template="reviews/new_review_moderator",
        success=True,
    ).exists()

    assert mock_send.called


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_review_removed_notifies_reviewer(mock_send, review):
    mock_send.return_value = 1

    ReviewNotificationService.review_removed(review)

    assert NotificationLog.objects.filter(
        recipient=review.reviewer,
        event_type=NotificationEventType.REVIEW,
        template="reviews/review_removed",
        success=True,
    ).exists()

    assert mock_send.called