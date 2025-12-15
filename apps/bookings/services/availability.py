from apps.bookings.models.booking import Booking, BookingStatus


def get_blocked_intervals(*, listing, start_date, end_date):
    """
    Returns a list of busy intervals within [start_date, end_date)
    """

    qs = Booking.objects.filter(
        listing=listing,
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).order_by("start_date")

    blocked = []
    for b in qs:
        blocked.append({
            "start": max(b.start_date, start_date),
            "end": min(b.end_date, end_date),
        })

    return blocked