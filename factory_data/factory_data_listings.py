from __future__ import annotations

import factory
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.listings.models import Listing, ListingStatus
from apps.properties.models import Property

from ._pool import make_picker

User = get_user_model()
ROLE_LANDLORD = "LANDLORD"


# pickers

pick_property = make_picker(
    lambda: Property.objects.all(),
    what="properties",
)

pick_landlord = make_picker(
    lambda: User.objects.filter(roles__name=ROLE_LANDLORD),
    what="landlords",
)


# factory

class ListingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Listing

    owner = factory.LazyFunction(pick_landlord)
    property = factory.LazyFunction(pick_property)

    title = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("paragraph", nb_sentences=3)

    price_eur = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
    )

    status = ListingStatus.ACTIVE
    is_deleted = False


# runner

@transaction.atomic
def run(listings_count: int = 80) -> None:
    print("Creating listings…")

    if not Property.objects.exists():
        raise RuntimeError("No properties found. Run properties seeder first.")

    if not User.objects.filter(roles__name=ROLE_LANDLORD).exists():
        raise RuntimeError("No landlords found. Run accounts seeder first.")

    ListingFactory.create_batch(listings_count)

    print(f"Listings generated: {listings_count}")