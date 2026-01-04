import pytest
from apps.listings.models import Listing
from apps.properties.models import Property


@pytest.fixture
def property(db, user):
    return Property.objects.create(
        owner=user,
        title="Test property",
        property_type="apartment",
        rooms=2,
    )


@pytest.fixture
def listing(db, user, property):
    return Listing.objects.create(
        owner=user,
        property=property,
        title="Test listing",
        price_eur=100,
        status=Listing.Status.DRAFT,
    )