import pytest
from datetime import timedelta
from django.utils import timezone

from apps.bookings.services.booking import create_booking
from apps.reviews.models import Review, PropertyRating
from apps.reviews.models.review import ReviewDirection, ReviewModerationStatus
from apps.accounts.models.role import Role


@pytest.fixture
def tenant_role(db):
    return Role.objects.create(name="tenant")


@pytest.fixture
def booking(db, user_factory, listing_factory):
    """
    Minimal valid booking for review tests.
    """
    landlord = user_factory(username="landlord_r", email="landlord_r@test.com")
    tenant = user_factory(username="tenant_r", email="tenant_r@test.com")

    listing = listing_factory(owner=landlord)

    booking = create_booking(
        listing=listing,
        tenant=tenant,
        start_date=timezone.localdate() + timedelta(days=1),
        end_date=timezone.localdate() + timedelta(days=3),
    )

    return booking


@pytest.fixture
def review(db, booking, tenant_role, property_rating):
    return Review.objects.create(
        booking=booking,
        reviewer=booking.tenant,
        target=booking.landlord,
        direction=ReviewDirection.TENANT_TO_LANDLORD,
        role=tenant_role,
        rating=4,
        property_rating=property_rating,  # ← КЛЮЧЕВО
        comment="Nice place",
        moderation_status=ReviewModerationStatus.APPROVED,
        is_hidden=False,
    )


@pytest.fixture
def property_rating(db, booking):
    return PropertyRating.objects.create(
        property=booking.listing.property,
    )