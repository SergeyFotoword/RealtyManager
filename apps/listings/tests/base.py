import itertools
from django.test import TestCase

from apps.accounts.models import User
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

    def create_location(self, **kwargs):
        defaults = {
            "state": GermanState.BE,
            "city": "Berlin",
            "postal_code": "10115",
        }
        defaults.update(kwargs)
        return Location.objects.create(**defaults)

    def create_property(self, **kwargs):
        location = kwargs.pop("location", None) or self.create_location()

        defaults = {
            "property_type": PropertyType.APARTMENT,
            "rooms": 2,
            "location": location,
        }
        defaults.update(kwargs)

        return Property.objects.create(**defaults)

    def create_listing(self, **kwargs):
        property_kwargs = {}

        for field in ["property_type", "rooms"]:
            if field in kwargs:
                property_kwargs[field] = kwargs.pop(field)

        property_obj = kwargs.pop("property", None) or self.create_property(**property_kwargs)

        owner = kwargs.pop("owner", None) or self.create_user()

        defaults = {
            "title": "Test listing",
            "price_eur": 1000,
            "property": property_obj,
            "owner": owner,
            "status": ListingStatus.ACTIVE,
        }
        defaults.update(kwargs)

        return Listing.objects.create(**defaults)