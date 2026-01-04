import itertools
from django.test import TestCase

from apps.accounts.models import User, Role
from apps.listings.models import Listing, ListingStatus
from apps.properties.models import Property, PropertyType
from apps.locations.models import Location, GermanState

_user_seq = itertools.count(1)

class BaseListingTest(TestCase):


    def create_user(self, **kwargs):
        i = next(_user_seq)
        defaults = {
            "username": f"user{i}",
            "email": f"user{i}@test.com",
            "password": "password123",
        }
        return User.objects.create_user(**defaults | kwargs)

    def create_landlord(self, **kwargs):
        user = self.create_user(**kwargs)

        landlord_role, _ = Role.objects.get_or_create(name="LANDLORD")
        user.roles.add(landlord_role)

        return user

    def create_location(self, **kwargs):
        defaults = {
            "country": "DE",
            "state": GermanState.BE,
            "city": "Berlin",
            "postal_code": "10115",
            "street": "",
            "house_number": "",
        }
        defaults.update(kwargs)

        obj, _ = Location.objects.get_or_create(
            country=defaults["country"],
            state=defaults["state"],
            city=defaults["city"],
            postal_code=defaults["postal_code"],
            defaults=defaults,
        )
        return obj

    def create_property(self, **kwargs):
        location = kwargs.pop("location", None) or self.create_location()
        owner = kwargs.pop("owner", None) or getattr(self, "user", None)

        if owner is None:
            raise RuntimeError(
                "create_property() called without owner. "
                "Pass owner explicitly or set self.user."
            )

        defaults = {
            "property_type": PropertyType.APARTMENT,
            "rooms": 2,
        }
        defaults.update(kwargs)

        return Property.objects.create(
            owner=owner,
            location=location,
            **defaults,
        )

    def create_listing(self, **kwargs):
        owner = kwargs.pop("owner", None) or self.create_user()

        property_kwargs = {}
        for field in ["property_type", "rooms"]:
            if field in kwargs:
                property_kwargs[field] = kwargs.pop(field)

        property_obj = kwargs.pop("property", None) or self.create_property(owner=owner, **property_kwargs)

        defaults = {
            "title": "Test listing",
            "price_eur": 1000,
            "property": property_obj,
            "owner": owner,
            "status": ListingStatus.ACTIVE,
        }
        defaults.update(kwargs)

        return Listing.objects.create(**defaults)