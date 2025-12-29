from typing import Any

from django.http import QueryDict

from apps.listings.constants import ListingOrderBy


def build_search_listings_kwargs(
    *,
    params: QueryDict,
    owner: Any | None = None,
    include_non_active: bool = False,
) -> dict:
    """
    Extract and normalize query params for search_listings().
    """

    order_by = params.get("order_by")
    if order_by not in ListingOrderBy.ALL:
        order_by = None

    return {
        "query": params.get("search") or params.get("q"),
        "price_min": params.get("price_min"),
        "price_max": params.get("price_max"),
        "rooms_min": params.get("rooms_min"),
        "rooms_max": params.get("rooms_max"),
        "property_type": params.get("property_type"),
        "amenities": params.get("amenities"),
        "city": params.get("city"),
        "has_images": (
            params.get("has_images") == "true"
            if params.get("has_images") is not None
            else None
        ),
        "order_by": order_by,
        "owner": owner,
        "include_non_active": include_non_active,
    }