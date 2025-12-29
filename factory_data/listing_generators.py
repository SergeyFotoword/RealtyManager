import random
from decimal import Decimal
from faker import Faker

from apps.listings.models import ListingStatus
from apps.properties.models import PropertyType

from .listing_rules import LISTING_RULES

faker = Faker()


def generate_status() -> str:
    r = random.random()
    cumulative = 0.0

    for status, weight in LISTING_RULES["status_distribution"]:
        cumulative += weight
        if r <= cumulative:
            return status

    return ListingStatus.ACTIVE


def generate_price(property_type: str) -> Decimal:
    min_p, max_p = LISTING_RULES["price_ranges"][property_type]
    return Decimal(random.randint(min_p, max_p))


def generate_title(property) -> str:
    city = property.location.city if hasattr(property.location, "city") else "City"

    if property.rooms:
        return f"{property.get_property_type_display()} · {property.rooms} rooms · {city}"
    return f"{property.get_property_type_display()} · {city}"


def generate_description(property) -> str:
    parts = []

    if property.area_sqm:
        parts.append(f"Area: {property.area_sqm} sqm.")

    if property.floor is not None and property.total_floors:
        parts.append(f"Floor {property.floor} of {property.total_floors}.")

    parts.append(faker.sentence(nb_words=12))

    return " ".join(parts)


def generate_soft_delete() -> bool:
    return random.random() < LISTING_RULES["deleted_ratio"]