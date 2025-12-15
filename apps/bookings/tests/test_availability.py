import datetime
from decimal import Decimal
from apps.bookings.services.availability import get_blocked_intervals
from apps.listings.models import Listing
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.accounts.models.user import User
from apps.bookings.tests.base import BaseBookingTest


class AvailabilityTest(BaseBookingTest):
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

    def test_blocked_intervals_are_returned(self):
        start = datetime.date(2025, 1, 1)
        end = datetime.date(2025, 1, 31)

        blocked = get_blocked_intervals(
            listing=self.listing,
            start_date=start,
            end_date=end,
        )

        self.assertEqual(blocked, [
            {"start": datetime.date(2025, 1, 1), "end": datetime.date(2025, 1, 5)}
        ])

    def test_checkout_day_is_free(self):
        start = datetime.date(2025, 1, 10)
        end = datetime.date(2025, 1, 15)

        blocked = get_blocked_intervals(
            listing=self.listing,
            start_date=start,
            end_date=end,
        )

        self.assertEqual(blocked, [])