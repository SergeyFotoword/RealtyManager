from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.bookings.models.booking import BookingStatus
from apps.bookings.services.booking import create_booking, confirm_booking, reject_booking, cancel_booking
from apps.notifications.models import NotificationLog
from apps.notifications.tasks import notify_expired_bookings


pytestmark = pytest.mark.django_db


@pytest.fixture
def booking_pending(user_factory, listing_factory):
    landlord = user_factory(username="landlord", email="landlord@test.com")
    tenant = user_factory(username="tenant", email="tenant@test.com")

    listing = listing_factory(owner=landlord)

    booking = create_booking(
        listing=listing,
        tenant=tenant,
        start_date=timezone.localdate() + timedelta(days=10),
        end_date=timezone.localdate() + timedelta(days=15),
    )
    return booking


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_pending_booking_notifies_landlord(mock_send, booking_pending):
    mock_send.return_value = 1
    booking = booking_pending

    assert NotificationLog.objects.filter(
        recipient=booking.landlord,
        template="booking/pending_created",
        success=True,
        context__tenant__isnull=False,  # tenant в контексте должен быть
    ).exists()


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_confirmed_booking_notifies_tenant(mock_send, booking_pending):
    mock_send.return_value = 1
    booking = booking_pending

    confirm_booking(booking=booking, landlord=booking.landlord)
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CONFIRMED

    assert NotificationLog.objects.filter(
        recipient=booking.tenant,
        template="booking/confirmed",
        success=True,
    ).exists()


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_rejected_booking_notifies_tenant(mock_send, booking_pending):
    mock_send.return_value = 1
    booking = booking_pending

    reject_booking(booking=booking, landlord=booking.landlord)

    assert booking.status == BookingStatus.REJECTED

    assert NotificationLog.objects.filter(
        recipient=booking.tenant,
        template="booking/rejected",
        success=True,
    ).exists()


@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_cancelled_booking_notifies_landlord(mock_send, booking_pending):
    mock_send.return_value = 1
    booking = booking_pending

    confirm_booking(booking=booking, landlord=booking.landlord)
    cancel_booking(booking=booking, user=booking.tenant)

    assert booking.status == BookingStatus.CANCELLED

    assert NotificationLog.objects.filter(
        recipient=booking.landlord,
        template="booking/cancelled",
        success=True,
    ).exists()



@patch("apps.notifications.services.base.EmailMultiAlternatives.send")
def test_notify_expired_bookings_sends_once_per_booking(mock_send, booking_pending):
    """
    notify_expired_bookings() шлёт письмо по EXPIRED и дедуплицирует по context.booking_id.
    """
    mock_send.return_value = 1
    booking = booking_pending

    # делаем booking EXPIRED
    booking.status = BookingStatus.EXPIRED
    booking.save(update_fields=["status"])

    notify_expired_bookings()
    notify_expired_bookings()  # второй раз не должен дублировать

    qs = NotificationLog.objects.filter(
        recipient=booking.tenant,
        template="booking/expired",
        context__booking_id=booking.id,
        success=True,
    )
    assert qs.count() == 1