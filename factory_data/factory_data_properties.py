from __future__ import annotations

import random
import factory
from django.db import transaction
from django.utils.text import slugify

from apps.properties.models import Property, Amenity, PropertyType
from apps.locations.models import Location

from ._pool import make_picker


AMENITIES = [
    "Wi-Fi",
    "Balcony",
    "Elevator",
    "Parking",
    "Air conditioning",
    "Washing machine",
    "Dishwasher",
    "Furnished",
    "Pet friendly",
    "Garden",
    "Storage room",
    "Basement",
]


def seed_amenities() -> None:
    """
    Reference data.
    Idempotent. No Factory here by design.
    """
    existing = set(Amenity.objects.values_list("name", flat=True))
    to_create = [name for name in AMENITIES if name not in existing]

    if not to_create:
        return

    Amenity.objects.bulk_create(
        [
            Amenity(
                name=name,
                slug=slugify(name),
                is_active=True,
            )
            for name in to_create
        ]
    )

# pickers

pick_location = make_picker(
    lambda: Location.objects.all(),
    what="locations",
)

pick_amenity = make_picker(
    lambda: Amenity.objects.filter(is_active=True),
    what="amenities",
)


# factory

class PropertyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Property

    property_type = factory.LazyFunction(lambda: random.choice(PropertyType.values))

    rooms = factory.LazyFunction(
        lambda: round(random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4, 5]), 1)
    )

    area_sqm = factory.LazyFunction(lambda: random.randint(25, 220))
    floor = factory.LazyFunction(lambda: random.choice([None, *range(0, 12)]))
    total_floors = factory.LazyFunction(lambda: random.choice([None, *range(1, 15)]))

    location = factory.LazyFunction(pick_location)

    @factory.post_generation
    def amenities(self, create, extracted, **kwargs):
        if not create:
            return

        all_amenities = list(Amenity.objects.filter(is_active=True))
        if not all_amenities:
            return

        k = random.randint(1, min(6, len(all_amenities)))
        self.amenities.add(*random.sample(all_amenities, k))


# runner

@transaction.atomic
def run(properties_count: int = 120) -> None:
    print("▶ Creating properties…")

    if not Location.objects.exists():
        raise RuntimeError("No locations found. Run locations seeder first.")

    seed_amenities()

    PropertyFactory.create_batch(properties_count)

    print(f"Properties generated: {properties_count}")