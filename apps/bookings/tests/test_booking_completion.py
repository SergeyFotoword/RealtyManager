import datetime
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.bookings.tests.base import BaseBookingTest
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.listings.models import Listing
from apps.bookings.models.booking import BookingStatus
from apps.bookings.services.lifecycle import complete_finished_bookings

User = get_user_model()


class BookingCompletionTest(BaseBookingTest):
    def setUp(self):

        self.landlord = User.objects.create_user(
            username="landlord",
            password="pass",
        )
        self.tenant = User.objects.create_user(
            username="tenant",
            password="pass",
        )

        self.location = Location.objects.create(
            country="DE",
            city="Berlin",
        )

        self.property = Property.objects.create(
            property_type=PropertyType.APARTMENT,
            rooms=Decimal("2.5"),
            location=self.location,
        )

        self.listing = Listing.objects.create(
            owner=self.landlord,
            property=self.property,
            title="Nice flat in Berlin",
            price_eur=Decimal("100.00"),
        )

        self.booking = self.create_confirmed_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 5),
        )

    def test_confirmed_booking_becomes_completed_after_end_date(self):
        today = datetime.date(2025, 1, 6)

        updated = complete_finished_bookings(today=today)

        self.booking.refresh_from_db()
        self.assertEqual(updated, 1)
        self.assertEqual(self.booking.status, BookingStatus.COMPLETED)