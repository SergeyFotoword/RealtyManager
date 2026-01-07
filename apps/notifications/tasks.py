from django.contrib.auth import get_user_model

from apps.bookings.models import Booking
from apps.bookings.models.booking import BookingStatus

from apps.notifications.models import NotificationLog
from apps.notifications.services.booking_notifications import (
    BookingNotificationService,
)
from apps.notifications.services.digest import DigestService

User = get_user_model()


def notify_expired_bookings() -> None:
    """
    Job for sending EXPIRED booking emails.

    Idempotent:
    - EXPIRED email is sent exactly once per booking
    - deduplicated via NotificationLog + booking_id
    """
    expired_qs = Booking.objects.filter(status=BookingStatus.EXPIRED)

    for booking in expired_qs.iterator():
        already_sent = NotificationLog.objects.filter(
            event_type="booking",
            template="booking/expired",
            context__booking_id=booking.id,
            success=True,
        ).exists()

        if already_sent:
            continue

        BookingNotificationService.expired(booking)


def run_digests() -> None:
    """
    Rolling 24h digest sender.
    Can be executed hourly via cron / celery beat.
    """
    users = User.objects.filter(
        notification_preferences__daily_digest=True,
        is_active=True,
    )

    for user in users.iterator():
        DigestService.send_daily_digest(user)

def send_daily_digest():
    """
    Cron-compatible task.
    """
    return DigestService.send_daily_digest()