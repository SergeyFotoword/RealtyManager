import datetime
import uuid
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.accounts.models.user import User
from apps.accounts.models.role import Role
from apps.locations.models import Location
from apps.properties.models import Property, PropertyType
from apps.listings.models import Listing
from apps.bookings.models.booking import Booking, BookingStatus
from apps.reviews.services.review import create_review

User = get_user_model()

class BaseReviewTest(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(username="landlord", password="pass")
        self.tenant = User.objects.create_user(username="tenant", password="pass")

        self.role_landlord = Role.objects.create(name="Landlord")
        self.role_tenant = Role.objects.create(name="Tenant")

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
            status=BookingStatus.COMPLETED,
        )

    def create_user(self, **kwargs):
        defaults = {
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "password": "testpass123",
            "is_active": True,
            **kwargs,
        }
        return User.objects.create_user(**defaults)


    def complete_stay(self):
        now = timezone.now()
        self.booking.checkin_at = now
        self.booking.checkout_at = now
        self.booking.save(update_fields=["checkin_at", "checkout_at"])

    def create_review_as_tenant(self, **kwargs):
        """
        Tenant → Landlord review.
        Used in moderation / edit / delete tests.
        """
        self.complete_stay()

        return create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=kwargs.get("rating", 5),
            role=kwargs.get("role", self.role_landlord),
            comment=kwargs.get("comment"),
        )

    def create_review_as_landlord(self):
        self.complete_stay()
        comment = self.kwargs.get("comment")
        return create_review(
            booking=self.booking,
            reviewer=self.landlord,
            rating=4,
            role=self.role_tenant,
            comment=comment or "Test review",
        )

