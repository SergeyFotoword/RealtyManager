import pytest
from apps.locations.models import Location, GermanState


@pytest.fixture
def location_factory(db):
    def factory(**kwargs):
        defaults = {
            "country": "DE",
            "state": GermanState.BE,
            "city": "Berlin",
            "postal_code": "10115",
        }
        defaults.update(kwargs)
        return Location.objects.create(**defaults)

    return factory