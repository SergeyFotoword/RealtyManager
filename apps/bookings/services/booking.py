import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.bookings.models.booking import Booking, BookingStatus
from apps.bookings.constants import (
    MAX_BOOKING_DAYS_AHEAD,
    MAX_STAY_DAYS,
    MIN_STAY_DAYS,
    CANCEL_DEADLINE_DAYS,
)


def _has_date_overlap(*, listing, start_date, end_date):
    return Booking.objects.filter(
        listing=listing,
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()

def create_booking(*, listing, tenant, start_date, end_date):
    today = timezone.localdate()
    max_start_date = today + datetime.timedelta(days=MAX_BOOKING_DAYS_AHEAD)

    if start_date > max_start_date:
        raise ValidationError(
            f"You can book only up to {MAX_BOOKING_DAYS_AHEAD} days ahead."
        )

    stay_length = (end_date - start_date).days
    if stay_length > MAX_STAY_DAYS:
        raise ValidationError(
            f"Maximum stay is {MAX_STAY_DAYS} nights."
        )

    if stay_length < MIN_STAY_DAYS:
        raise ValidationError("Minimum stay is 1 night.")

    # You can't reserve your own
    if listing.owner_id == tenant.id:
        raise ValidationError("You cannot book your own listing.")

    # 2. Checking date intersections
    if _has_date_overlap(
            listing=listing,
            start_date=start_date,
            end_date=end_date,
    ):
        raise ValidationError(
            "This listing is already booked for the selected dates."
        )

    booking = Booking.objects.create(
        listing=listing,
        tenant=tenant,
        landlord=listing.owner,
        start_date=start_date,
        end_date=end_date,
    )
    return booking


def confirm_booking(*, booking, landlord):
    if booking.status != BookingStatus.PENDING:
        raise ValidationError("Only pending bookings can be confirmed.")

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can confirm this booking.")

    booking.status = BookingStatus.CONFIRMED
    booking.confirmed_at = timezone.now()
    booking.save(update_fields=["status", "confirmed_at"])


def reject_booking(*, booking, landlord):
    if booking.status != BookingStatus.PENDING:
        raise ValidationError("Only pending bookings can be rejected.")

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can reject this booking.")

    booking.status = BookingStatus.REJECTED
    booking.save(update_fields=["status"])


def cancel_booking(*, booking, user):
    if booking.tenant_id != user.id:
        raise ValidationError("You can cancel only your own booking.")

    if booking.status not in (
        BookingStatus.PENDING,
        BookingStatus.CONFIRMED,
    ):
        raise ValidationError("This booking cannot be cancelled.")

    today = timezone.localdate()
    cancel_deadline = booking.start_date - timezone.timedelta(days=CANCEL_DEADLINE_DAYS)

    if today >= cancel_deadline:
        raise ValidationError(
            f"Cancellation is allowed only up to {CANCEL_DEADLINE_DAYS} days before check-in."
        )

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])