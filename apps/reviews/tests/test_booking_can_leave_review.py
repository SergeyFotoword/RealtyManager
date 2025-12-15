import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models.user import User
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.listings.models import Listing
from apps.bookings.models.booking import Booking, BookingStatus


class BookingCanLeaveReviewPropertyTest(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(username="landlord", password="pass")
        self.tenant = User.objects.create_user(username="tenant", password="pass")

        self.location = Location.objects.create(country="DE", city="Berlin")
        self.property = Property.objects.create(
            property_type=PropertyType.APARTMENT,
            rooms=Decimal("2.5"),
            location=self.location,
        )
        self.listing = Listing.objects.create(
            owner=self.landlord,
            property=self.property,
            title="Nice flat",
            price_eur=Decimal("100.00"),
        )

        self.booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            landlord=self.landlord,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 5),
            status=BookingStatus.CONFIRMED,
        )

    def test_can_leave_review_is_false_without_checkin_and_checkout(self):
        self.assertFalse(self.booking.can_leave_review)

    def test_can_leave_review_is_false_with_checkin_only(self):
        self.booking.checkin_at = timezone.now()
        self.booking.save(update_fields=["checkin_at"])
        self.assertFalse(self.booking.can_leave_review)

    def test_can_leave_review_is_true_with_checkin_and_checkout(self):
        now = timezone.now()
        self.booking.checkin_at = now
        self.booking.checkout_at = now
        self.booking.save(update_fields=["checkin_at", "checkout_at"])
        self.assertTrue(self.booking.can_leave_review)

    def test_can_leave_review_is_false_with_checkout_only(self):
        self.booking.checkout_at = timezone.now()
        self.booking.save(update_fields=["checkout_at"])
        self.assertFalse(self.booking.can_leave_review)