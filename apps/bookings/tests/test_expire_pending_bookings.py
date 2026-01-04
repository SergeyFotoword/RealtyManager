import datetime

import pytest
from django.utils import timezone

from apps.bookings.models.booking import Booking, BookingStatus
from apps.bookings.management.commands.expire_pending_bookings import Command
from apps.bookings.services.booking import create_booking
from apps.bookings.services.availability import get_blocked_intervals


pytestmark = pytest.mark.django_db


def test_pending_booking_expires_and_releases_dates(
    user_factory,
    listing_factory,
):
    """
    GIVEN:
        - a PENDING booking older than TTL
    WHEN:
        - expire_pending_bookings command is executed
    THEN:
        - booking status becomes EXPIRED
        - booking no longer blocks availability
    """

    # --- setup ---
    landlord = user_factory()
    tenant = user_factory()
    listing = listing_factory(owner=landlord)

    start_date = timezone.localdate() + datetime.timedelta(days=5)
    end_date = start_date + datetime.timedelta(days=3)

    booking = create_booking(
        listing=listing,
        tenant=tenant,
        start_date=start_date,
        end_date=end_date,
    )

    assert booking.status == BookingStatus.PENDING

    # artificially move booking creation time to the past
    past = timezone.now() - datetime.timedelta(hours=25)
    Booking.objects.filter(pk=booking.pk).update(created_at=past)

    # sanity check: booking blocks availability BEFORE expire
    blocked_before = get_blocked_intervals(
        listing=listing,
        start_date=start_date,
        end_date=end_date,
    )
    assert blocked_before, "Booking must block dates before expiration"

    # --- act ---
    cmd = Command()
    cmd.handle(ttl_hours=24)

    booking.refresh_from_db()

    # --- assert ---
    assert booking.status == BookingStatus.EXPIRED

    blocked_after = get_blocked_intervals(
        listing=listing,
        start_date=start_date,
        end_date=end_date,
    )
    assert not blocked_after, "Expired booking must NOT block dates"