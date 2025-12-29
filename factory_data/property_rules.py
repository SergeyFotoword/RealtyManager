from decimal import Decimal
from apps.properties.models import PropertyType


PROPERTY_RULES = {
    PropertyType.APARTMENT: {
        "rooms": {"min": Decimal("1"), "max": Decimal("6")},
        "area_sqm": {"min": 20, "max": 250},
        "floor": {"min": 0, "max": 30},
        "total_floors": {"min": 1, "max": 40},
        "amenities": True,
    },

    PropertyType.STUDIO: {
        "rooms": {"fixed": Decimal("1")},
        "area_sqm": {"min": 18, "max": 80},
        "floor": {"min": 0, "max": 20},
        "total_floors": {"min": 1, "max": 30},
        "amenities": True,
    },

    PropertyType.ROOM: {
        "rooms": {"fixed": Decimal("1")},
        "area_sqm": {"min": 10, "max": 40},
        "floor": {"min": 0, "max": 10},
        "total_floors": {"min": 1, "max": 15},
        "amenities": False,
    },

    PropertyType.MAISONETTE: {
        "rooms": {"min": Decimal("2"), "max": Decimal("6")},
        "area_sqm": {"min": 60, "max": 250},
        "floor": {"min": 0, "max": 10},
        "total_floors": {"min": 2, "max": 10},
        "amenities": True,
        "special": "multi_level_unit",
    },

    PropertyType.PENTHOUSE: {
        "rooms": {"min": Decimal("2"), "max": Decimal("6")},
        "area_sqm": {"min": 80, "max": 400},
        "floor": "TOP",
        "total_floors": {"min": 3, "max": 60},
        "amenities": True,
        "special": "top_floor",
    },

    PropertyType.HOUSE: {
        "rooms": {"min": Decimal("2"), "max": Decimal("10")},
        "area_sqm": {"min": 60, "max": 400},
        "floor": None,
        "total_floors": {"min": 1, "max": 3},
        "amenities": True,
    },

    PropertyType.OFFICE: {
        "rooms": {"min": Decimal("1"), "max": Decimal("20")},
        "area_sqm": {"min": 30, "max": 1000},
        "floor": {"min": 0, "max": 50},
        "total_floors": {"min": 1, "max": 80},
        "amenities": True,
    },

    PropertyType.RETAIL: {
        "rooms": None,
        "area_sqm": {"min": 20, "max": 2000},
        "floor": {"min": 0, "max": 5},
        "total_floors": {"min": 1, "max": 10},
        "amenities": False,
    },

    PropertyType.WAREHOUSE: {
        "rooms": None,
        "area_sqm": {"min": 50, "max": 10000},
        "floor": None,
        "total_floors": None,
        "amenities": False,
    },

    PropertyType.PARKING: {
        "rooms": None,
        "area_sqm": {"min": 10, "max": 40},
        "floor": {"min": -5, "max": 10}, # underground levels
        "total_floors": {"min": 1, "max": 10},
        "amenities": False,
    },

    PropertyType.LAND: {
        "rooms": None,
        "area_sqm": {"min": 100, "max": 100000},
        "floor": None,
        "total_floors": None,
        "amenities": False,
    },
}