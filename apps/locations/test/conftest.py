import pytest
from apps.locations.models import Location
from apps.locations.constants import GermanState


@pytest.fixture
def berlin_location(db):
    """
    Canonical location for testing.
    Reused, NOT created each time.
    """
    obj, _ = Location.objects.get_or_create(
        country="DE",
        state=GermanState.BE,
        city="Berlin",
        postal_code="10115",
        defaults={
            "street": "",
            "house_number": "",
            "lat": None,
            "lng": None,
        },
    )
    return obj