import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.locations.models import Location, GermanState
from apps.properties.models import Property, PropertyType
from apps.listings.models import Listing, ListingStatus

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
    )


@pytest.fixture
def user_factory(db):
    def factory(**kwargs):
        username = kwargs.pop("username", None)
        if username is None:
            username = f"user_{User.objects.count()+1}"

        email = kwargs.pop("email", None)
        if email is None:
            email = f"{username}@test.com"

        password = kwargs.pop("password", "password123")
        return User.objects.create_user(username=username, email=email, password=password, **kwargs)
    return factory

@pytest.fixture
def staff_moderator(user_factory):
    return user_factory(username="moderator", email="moderator@test.com", is_staff=True, is_active=True)


@pytest.fixture
def property_factory(db, user_factory, location_factory):
    def factory(**kwargs):
        owner = kwargs.pop("owner", None) or user_factory()
        location = kwargs.pop("location", None) or location_factory()

        return Property.objects.create(
            owner=owner,
            location=location,
            property_type=kwargs.pop("property_type", PropertyType.APARTMENT),
            rooms=kwargs.pop("rooms", 2),
            **kwargs,
        )
    return factory


@pytest.fixture
def listing_factory(db, property_factory, user_factory):
    def factory(**kwargs):
        owner = kwargs.pop("owner", None) or user_factory()
        prop = kwargs.pop("property", None) or property_factory(owner=owner)
        return Listing.objects.create(
            owner=owner,
            property=prop,
            title=kwargs.pop("title", "Test listing"),
            price_eur=kwargs.pop("price_eur", 100),
            status=kwargs.pop("status", ListingStatus.DRAFT),
            **kwargs,
        )
    return factory


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def location_factory(db):
    def factory(**kwargs):
        return Location.objects.create(
            country=kwargs.pop("country", "DE"),
            state=kwargs.pop("state", GermanState.BE),
            city=kwargs.pop("city", "Berlin"),
            postal_code=kwargs.pop("postal_code", "10115"),
            street=kwargs.pop("street", ""),
            house_number=kwargs.pop("house_number", ""),
        )
    return factory