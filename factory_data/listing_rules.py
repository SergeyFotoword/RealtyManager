from apps.listings.models import ListingStatus
from apps.properties.models import PropertyType


LISTING_RULES = {
    "status_distribution": [
        (ListingStatus.ACTIVE, 0.60),
        (ListingStatus.DRAFT, 0.25),
        (ListingStatus.INACTIVE, 0.15),
    ],

    "deleted_ratio": 0.05,

    "price_ranges": {
        PropertyType.ROOM: (300, 800),
        PropertyType.STUDIO: (500, 1200),
        PropertyType.APARTMENT: (800, 3000),
        PropertyType.MAISONETTE: (1200, 4000),
        PropertyType.PENTHOUSE: (2500, 9000),
        PropertyType.HOUSE: (1000, 6000),
        PropertyType.OFFICE: (500, 8000),
        PropertyType.RETAIL: (700, 12000),
        PropertyType.WAREHOUSE: (800, 15000),
        PropertyType.PARKING: (50, 250),
        PropertyType.LAND: (100, 3000),
    },
}