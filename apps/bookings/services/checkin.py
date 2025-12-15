from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.bookings.models.booking import BookingStatus


def confirm_checkin(*, booking, landlord):
    if booking.status != BookingStatus.CONFIRMED:
        raise ValidationError("Check-in allowed only for confirmed bookings.")

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can confirm check-in.")

    if booking.checkin_at is not None:
        raise ValidationError("Check-in already confirmed.")

    booking.checkin_at = timezone.now()
    booking.save(update_fields=["checkin_at"])


def confirm_checkout(*, booking, landlord):
    if booking.checkin_at is None:
        raise ValidationError("Checkout without check-in is not allowed.")

    if booking.listing.owner_id != landlord.id:
        raise ValidationError("Only the listing owner can confirm checkout.")

    if booking.checkout_at is not None:
        raise ValidationError("Checkout already confirmed.")

    booking.checkout_at = timezone.now()
    booking.save(update_fields=["checkout_at"])