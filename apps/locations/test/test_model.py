import pytest
from django.db import IntegrityError
from apps.locations.models import GermanState, Location


@pytest.mark.django_db
def test_location_created(location_factory):
    loc = location_factory()
    assert loc.id is not None


@pytest.mark.django_db
def test_location_uses_iso_country_code(location_factory):
    loc = location_factory()
    assert loc.country == "DE"
    assert len(loc.country) == 2


@pytest.mark.django_db
def test_location_state_is_enum(location_factory):
    loc = location_factory(state=GermanState.BY)
    assert loc.state == GermanState.BY


@pytest.mark.django_db
def test_location_unique_constraint(location_factory):
    location_factory()

    with pytest.raises(IntegrityError):
        location_factory()


@pytest.mark.django_db
def test_location_str_representation(location_factory):
    loc = location_factory(
        postal_code="10115",
        city="Berlin",
        state=GermanState.BE,
    )
    assert str(loc) == "10115 Berlin, BE"