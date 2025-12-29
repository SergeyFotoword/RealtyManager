from __future__ import annotations

import random
import factory
from django.db import transaction

from apps.locations.models import Location, GermanState


GERMAN_CITIES = [
    ("Berlin", "10115"),
    ("Hamburg", "20095"),
    ("Munich", "80331"),
    ("Cologne", "50667"),
    ("Frankfurt am Main", "60311"),
    ("Stuttgart", "70173"),
    ("Düsseldorf", "40213"),
    ("Leipzig", "04109"),
    ("Dresden", "01067"),
    ("Hannover", "30159"),
]


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    country = "DE"
    state = factory.LazyFunction(lambda: random.choice(GermanState.values))

    city = factory.LazyFunction(lambda: random.choice(GERMAN_CITIES)[0])
    postal_code = factory.LazyFunction(lambda: random.choice(GERMAN_CITIES)[1])

    street = factory.Faker("street_name")
    house_number = factory.Faker("building_number")

    lat = factory.Faker("latitude")
    lng = factory.Faker("longitude")


@transaction.atomic
def run(locations_count: int = 60) -> None:
    print("▶ Creating locations…")

    LocationFactory.create_batch(locations_count)

    print(f"Locations generated: {locations_count}")