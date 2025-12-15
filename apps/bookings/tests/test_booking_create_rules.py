import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.bookings.services.booking import create_booking
from apps.bookings.constants import MAX_STAY_DAYS
from apps.accounts.models.user import User
from apps.listings.models import Listing
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType


class BookingCreateRulesTest(TestCase):
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

    def test_booking_too_long_is_blocked(self):
        start = timezone.localdate() + datetime.timedelta(days=10)
        end = start + datetime.timedelta(days=MAX_STAY_DAYS + 1)

        with self.assertRaises(ValidationError):
            create_booking(
                listing=self.listing,
                tenant=self.tenant,
                start_date=start,
                end_date=end,
            )