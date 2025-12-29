from decimal import Decimal, InvalidOperation
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.listings.constants import ListingOrderBy

from apps.listings.models.models import Listing, ListingStatus


def _to_decimal(val):
    if val is None or val == "":
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _to_int(val):
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def search_listings(
    *,
    query: str | None = None,
    price_min=None,
    price_max=None,
    rooms_min=None,
    rooms_max=None,
    property_type=None,
    amenities: str | None = None,
    city: str | None = None,
    has_images: bool | None = None,
    order_by: str | None = None,
    owner=None,
    include_non_active: bool = False,
):
    qs = Listing.objects.filter(is_deleted=False).select_related("property", "property__location")

    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # public: only ACTIVE
    if not include_non_active:
        qs = qs.filter(status=ListingStatus.ACTIVE)

    # my: any status
    if owner is not None:
        qs = qs.filter(owner=owner)

    price_min = _to_decimal(price_min)
    price_max = _to_decimal(price_max)
    if price_min is not None:
        qs = qs.filter(price_eur__gte=price_min)
    if price_max is not None:
        qs = qs.filter(price_eur__lte=price_max)

    rooms_min = _to_int(rooms_min)
    rooms_max = _to_int(rooms_max)
    if rooms_min is not None:
        qs = qs.filter(property__rooms__gte=rooms_min)
    if rooms_max is not None:
        qs = qs.filter(property__rooms__lte=rooms_max)

    if property_type:
        qs = qs.filter(property__property_type=property_type)

    if city:
        qs = qs.filter(property__location__city__icontains=city)

    if amenities:
        slugs = [s.strip() for s in amenities.split(",") if s.strip()]
        if slugs:
            qs = qs.filter(property__amenities__slug__in=slugs).distinct()

    # listings with/without images
    if has_images is True:
        qs = qs.filter(images__isnull=False).distinct()
    elif has_images is False:
        qs = qs.filter(images__isnull=True)

    if order_by == ListingOrderBy.PRICE_ASC:
        qs = qs.order_by("price_eur")

    elif order_by == ListingOrderBy.PRICE_DESC:
        qs = qs.order_by("-price_eur")

    elif order_by == ListingOrderBy.CREATED_NEW:
        qs = qs.order_by("-created_at")

    elif order_by == ListingOrderBy.CREATED_OLD:
        qs = qs.order_by("created_at")

    elif order_by == ListingOrderBy.POPULAR:
        qs = qs.annotate(
            popularity=Count("views")
        ).order_by("-popularity", "-created_at")

    elif order_by == ListingOrderBy.POPULAR_UNIQ:
        qs = qs.annotate(
            popularity=Count("views__user", distinct=True)
        ).order_by("-popularity", "-created_at")

    elif order_by == ListingOrderBy.POPULAR_7D:
        since = timezone.now() - timedelta(days=7)
        qs = qs.annotate(
            popularity=Count(
                "views",
                filter=Q(views__created_at__gte=since),
            )
        ).order_by("-popularity", "-created_at")

    elif order_by == ListingOrderBy.POPULAR_30D:
        since = timezone.now() - timedelta(days=30)
        qs = qs.annotate(
            popularity=Count(
                "views",
                filter=Q(views__created_at__gte=since),
            )
        ).order_by("-popularity", "-created_at")

    return qs