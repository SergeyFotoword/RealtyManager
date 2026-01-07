import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

from apps.bookings.tests.base import BaseBookingTest
from apps.bookings.services.booking import cancel_booking
from apps.bookings.constants import CANCEL_DEADLINE_DAYS
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.listings.models import Listing
from apps.accounts.models.user import User
from apps.bookings.models.booking import BookingStatus


class BookingCancelDeadlineTest(BaseBookingTest):
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

    def test_cancel_before_deadline_is_allowed(self):
        start_date = timezone.localdate() + datetime.timedelta(
            days=CANCEL_DEADLINE_DAYS + 2
        )

        booking = self.create_confirmed_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=3),
        )

        cancel_booking(
            booking=booking,
            user=self.tenant,
        )

        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_cancel_on_deadline_day_is_blocked(self):
        start_date = timezone.localdate() + datetime.timedelta(
            days=CANCEL_DEADLINE_DAYS
        )

        booking = self.create_confirmed_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=3),
        )

        with self.assertRaises(ValidationError):
            cancel_booking(
                booking=booking,
                user=self.tenant,
            )