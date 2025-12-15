from django.utils import timezone
from apps.bookings.models.booking import Booking, BookingStatus


def complete_finished_bookings(*, today=None) -> int:
    """
    Translates CONFIRMED → COMPLETED if the departure date has already passed.
    Returns the number of updated records.
    """
    if today is None:
        today = timezone.localdate()

    qs = Booking.objects.filter(
        status=BookingStatus.CONFIRMED,
        end_date__lt=today,
    )

    return qs.update(status=BookingStatus.COMPLETED)