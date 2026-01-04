import pytest
from datetime import date, timedelta
from apps.bookings.models import Booking


@pytest.fixture
def booking_dates():
    today = date.today()
    return {
        "start_date": today + timedelta(days=1),
        "end_date": today + timedelta(days=5),
    }


@pytest.fixture
def booking(db, user, listing, booking_dates):
    return Booking.objects.create(
        user=user,
        listing=listing,
        start_date=booking_dates["start_date"],
        end_date=booking_dates["end_date"],
        status=Booking.Status.PENDING,
    )