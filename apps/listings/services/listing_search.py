from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.listings.models import Listing, ListingStatus


def search_listings(
    *,
    owner=None,
    include_non_active=False,
    order_by=None,
    search=None,
    query=None,
    city=None,
    state=None,
    amenities=None,
    price_min=None,
    price_max=None,
    rooms_min=None,
    property_type=None,
    **_ignored,  # ← КРИТИЧНО: не ломаем контракт
):
    """
    Central listings search service.

    IMPORTANT:
    - Must accept ALL kwargs coming from build_search_listings_kwargs
    - Unknown filters are ignored safely
    """

    qs = Listing.objects.all()

    # -------------------------------------------------
    # 1. SOFT DELETE
    # -------------------------------------------------
    qs = qs.filter(deleted_at__isnull=True)

    # -------------------------------------------------
    # 2. OWNER / STATUS
    # -------------------------------------------------
    if owner is not None:
        qs = qs.filter(owner=owner)
        if not include_non_active:
            qs = qs.filter(status=ListingStatus.ACTIVE)
    else:
        qs = qs.filter(status=ListingStatus.ACTIVE)

    # -------------------------------------------------
    # 3. SEARCH (query OR search)
    # -------------------------------------------------
    term = search or query
    if term:
        qs = qs.filter(
            Q(title__icontains=term)
            | Q(description__icontains=term)
        )

    # -------------------------------------------------
    # 4. LOCATION
    # -------------------------------------------------
    if city:
        qs = qs.filter(property__location__city__iexact=city)

    if state:
        qs = qs.filter(property__location__state__iexact=state)

    # -------------------------------------------------
    # 5. AMENITIES
    # -------------------------------------------------
    if amenities:
        qs = qs.filter(property__amenities__slug__in=[amenities]).distinct()

    # -------------------------------------------------
    # 6. NUMERIC FILTERS
    # -------------------------------------------------
    if price_min is not None:
        qs = qs.filter(price_eur__gte=price_min)

    if price_max is not None:
        qs = qs.filter(price_eur__lte=price_max)

    if rooms_min is not None:
        qs = qs.filter(property__rooms__gte=rooms_min)

    if property_type:
        qs = qs.filter(property__property_type=property_type)

    # -------------------------------------------------
    # 7. ORDERING (STRING BASED)
    # -------------------------------------------------
    if order_by == "price_asc":
        qs = qs.order_by("price_eur")

    elif order_by == "price_desc":
        qs = qs.order_by("-price_eur")

    elif order_by == "popular":
        qs = qs.annotate(
            total_views=Count("views")
        ).order_by("-total_views", "-created_at")

    elif order_by == "popular_7d":
        since = timezone.now() - timedelta(days=7)
        qs = qs.annotate(
            total_views=Count(
                "views",
                filter=Q(views__created_at__gte=since),
            )
        ).order_by("-total_views", "-created_at")

    elif order_by == "popular_30d":
        since = timezone.now() - timedelta(days=30)
        qs = qs.annotate(
            total_views=Count(
                "views",
                filter=Q(views__created_at__gte=since),
            )
        ).order_by("-total_views", "-created_at")

    else:
        qs = qs.order_by("-created_at")

    return qs