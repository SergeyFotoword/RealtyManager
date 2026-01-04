import pytest
from apps.properties.models import Property

@pytest.fixture
def property(db, user, berlin_location):
    return Property.objects.create(
        owner=user,
        location=berlin_location,
        title="Test property",
        property_type="apartment",
        rooms=2,
    )