from django.utils import timezone
from django.db import transaction

from apps.bookings.models.booking import Booking, BookingStatus


def expire_pending_bookings(*, ttl_hours: int = 24) -> int:
    """
    Expires PENDING bookings older than ttl_hours.

    Rules:
    - Only PENDING bookings are affected
    - Booking becomes EXPIRED
    - Dates are released automatically
    - Returns number of expired bookings
    """

    now = timezone.now()
    cutoff = now - timezone.timedelta(hours=ttl_hours)

    with transaction.atomic():
        qs = Booking.objects.select_for_update().filter(
            status=BookingStatus.PENDING,
            created_at__lt=cutoff,
        )

        updated = qs.update(
            status=BookingStatus.EXPIRED,
            expired_at=now,
        )

    return updated