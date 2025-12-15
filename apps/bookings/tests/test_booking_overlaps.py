import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.bookings.services.booking import create_booking
from apps.bookings.tests.base import BaseBookingTest
from apps.listings.models import Listing
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.accounts.models.user import User


class BookingOverlapTest(BaseBookingTest):
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

    def test_overlap_is_blocked(self):
        self.create_confirmed_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 5),
        )

        with self.assertRaises(ValidationError):
            create_booking(
                listing=self.listing,
                tenant=self.tenant,
                start_date=datetime.date(2025, 1, 4),
                end_date=datetime.date(2025, 1, 10),
            )

    def test_checkout_day_is_allowed(self):
        self.create_confirmed_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 5),
        )

        create_booking(
            listing=self.listing,
            tenant=self.tenant,
            start_date=datetime.date(2025, 1, 5),
            end_date=datetime.date(2025, 1, 10),
        )