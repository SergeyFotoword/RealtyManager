from apps.bookings.models import BookingStatus

BOOKING_RULES = {
    "status_distribution": [
        (BookingStatus.COMPLETED, 0.35),
        (BookingStatus.CONFIRMED, 0.25),
        (BookingStatus.PENDING, 0.15),
        (BookingStatus.REJECTED, 0.15),
        (BookingStatus.CANCELLED, 0.10),
    ],
    "min_days": 1,
    "max_days": 30,
}