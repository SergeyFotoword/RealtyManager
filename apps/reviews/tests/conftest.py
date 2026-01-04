import pytest
from apps.reviews.models import Review


@pytest.fixture
def review(db, booking, user):
    return Review.objects.create(
        booking=booking,
        author=user,
        rating=4,
        comment="Nice place",
        is_public=True,
    )