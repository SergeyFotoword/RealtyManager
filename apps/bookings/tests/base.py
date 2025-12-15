from django.test import TestCase
from apps.bookings.models.booking import BookingStatus
from apps.bookings.services.booking import create_booking

class BaseBookingTest(TestCase):

    def create_confirmed_booking(
        self,
        *,
        listing,
        tenant,
        start_date,
        end_date,
    ):
        booking = create_booking(
            listing=listing,
            tenant=tenant,
            start_date=start_date,
            end_date=end_date,
        )
        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status"])
        return booking