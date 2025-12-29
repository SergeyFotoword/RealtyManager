import random
from decimal import Decimal
from apps.properties.models import PropertyType
from .property_rules import PROPERTY_RULES


def generate_rooms(property_type: str) -> Decimal:
    rules = PROPERTY_RULES[property_type]["rooms"]

    # rooms not applicable → 0 (DB-safe)
    if rules is None:
        return Decimal("0")

    if "fixed" in rules:
        return Decimal(rules["fixed"])

    min_r, max_r = rules["min"], rules["max"]

    # 0.5 steps (DE standard)
    possible = [
        Decimal(x) / 2
        for x in range(int(min_r * 2), int(max_r * 2) + 1)
    ]
    return random.choice(possible)


def generate_area(property_type: str) -> int:
    rules = PROPERTY_RULES[property_type]["area_sqm"]

    # area always required in DB
    if rules is None:
        return 0

    return random.randint(rules["min"], rules["max"])


def generate_floors(property_type: str) -> tuple[int | None, int | None]:
    rules = PROPERTY_RULES[property_type]

    floor_rule = rules["floor"]
    total_rule = rules["total_floors"]

    if floor_rule is None and total_rule is None:
        return None, None

    total_floors = None
    if isinstance(total_rule, dict):
        total_floors = random.randint(
            total_rule["min"], total_rule["max"]
        )

    if floor_rule == "TOP":
        return total_floors, total_floors

    if isinstance(floor_rule, dict):
        floor = random.randint(
            floor_rule["min"], floor_rule["max"]
        )

        if total_floors is not None:
            floor = min(floor, total_floors)

        return floor, total_floors

    return None, total_floors


def amenities_allowed(property_type: str) -> bool:
    return bool(PROPERTY_RULES[property_type]["amenities"])


def generate_property_data(property_type: str) -> dict:
    floor, total_floors = generate_floors(property_type)

    return {
        "property_type": property_type,
        "rooms": generate_rooms(property_type),      # NEVER None
        "area_sqm": generate_area(property_type),    # NEVER None
        "floor": floor,
        "total_floors": total_floors,
    }