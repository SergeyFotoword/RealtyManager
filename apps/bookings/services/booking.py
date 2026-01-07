import datetime

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.bookings.models.booking import Booking, BookingStatus
from apps.bookings.constants import (
    MAX_BOOKING_DAYS_AHEAD,
    MAX_STAY_DAYS,
    MIN_STAY_DAYS,
    CANCEL_DEADLINE_DAYS,
)


def _has_date_overlap(*, listing, start_date, end_date) -> bool:
    """
    Checks if there is any PENDING or CONFIRMED booking
    overlapping with the given date range.
    """
    return Booking.objects.filter(
        listing=listing,
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()


def create_booking(*, listing, tenant, start_date, end_date) -> Booking:
    """
    Create a booking request.

    Business rules:
    - booking can be made only up to MAX_BOOKING_DAYS_AHEAD
    - stay length must be between MIN_STAY_DAYS and MAX_STAY_DAYS
    - tenant cannot book own listing
    - no date overlap with existing PENDING or CONFIRMED bookings
    """

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

    # Tenant cannot reserve own listing
    if listing.owner_id == tenant.id:
        raise ValidationError("You cannot book your own listing.")

    # Date intersection check (PENDING + CONFIRMED)
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
        status=BookingStatus.PENDING,
    )

    # notice to landlord
    from apps.notifications.services.booking_notifications import BookingNotificationService
    BookingNotificationService.pending_created(booking)

    return booking


def confirm_booking(*, booking: Booking, landlord):
    """
    Confirm a booking.

    Rules:
    - only listing owner can confirm
    - booking must be PENDING
    - EXPIRED bookings cannot be confirmed
    - operation is atomic and idempotent
    """

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can confirm this booking.")

    # EXPIRED — hard stop
    if booking.status == BookingStatus.EXPIRED:
        raise ValidationError("Booking has expired.")

    # Idempotency: already confirmed → ok
    if booking.status == BookingStatus.CONFIRMED:
        return booking

    if booking.status != BookingStatus.PENDING:
        raise ValidationError("Only pending bookings can be confirmed.")

    # Race-condition protection
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(pk=booking.pk)

        if booking.status == BookingStatus.EXPIRED:
            raise ValidationError("Booking has expired.")

        if booking.status == BookingStatus.CONFIRMED:
            return booking

        if booking.status != BookingStatus.PENDING:
            raise ValidationError("Only pending bookings can be confirmed.")

        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = timezone.now()
        booking.save(update_fields=["status", "confirmed_at"])

    from apps.notifications.services.booking_notifications import BookingNotificationService
    BookingNotificationService.confirmed(booking)

    return booking


def reject_booking(*, booking: Booking, landlord):
    """
    Reject a pending booking by listing owner.
    """

    if booking.status == BookingStatus.EXPIRED:
        raise ValidationError("Booking has expired.")

    if booking.status != BookingStatus.PENDING:
        raise ValidationError("Only pending bookings can be rejected.")

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can reject this booking.")

    booking.status = BookingStatus.REJECTED
    booking.save(update_fields=["status"])

    from apps.notifications.services.booking_notifications import BookingNotificationService
    BookingNotificationService.rejected(booking)

    return booking

def cancel_booking(*, booking: Booking, user):
    """
    Cancel a booking by tenant.

    Rules:
    - only tenant can cancel own booking
    - only PENDING or CONFIRMED bookings
    - cancellation deadline enforced
    """

    if booking.status == BookingStatus.EXPIRED:
        raise ValidationError("Booking has expired.")

    if booking.tenant_id != user.id:
        raise ValidationError("You can cancel only your own booking.")

    if booking.status not in (
        BookingStatus.PENDING,
        BookingStatus.CONFIRMED,
    ):
        raise ValidationError("This booking cannot be cancelled.")

    today = timezone.localdate()
    cancel_deadline = booking.start_date - timezone.timedelta(
        days=CANCEL_DEADLINE_DAYS
    )

    if today >= cancel_deadline:
        raise ValidationError(
            f"Cancellation is allowed only up to "
            f"{CANCEL_DEADLINE_DAYS} days before check-in."
        )

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.save(update_fields=["status", "cancelled_at"])

    from apps.notifications.services.booking_notifications import BookingNotificationService
    BookingNotificationService.cancelled(booking)

    return booking