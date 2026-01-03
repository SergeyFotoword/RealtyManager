from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.listings.serializers.listing_list import ListingListSerializer
from apps.listings.services.listing_search import search_listings
from apps.listings.services.search_history import save_search_query
from apps.listings.utils.search_params import build_search_listings_kwargs
from apps.listings.constants import ListingOrderBy


@extend_schema(
    summary="Public listings search",
    description=(
        "Search and filter public real estate listings.\n\n"
        "Supports:\n"
        "- Full-text search by title and description\n"
        "- Filters by price, rooms, city, amenities\n"
        "- Multiple ordering strategies (price, date, popularity)\n\n"
        "Available ordering options can be retrieved via OPTIONS request."
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            description="Full-text search query (title and description)",
        ),
        OpenApiParameter(
            name="price_min",
            description="Minimum price in EUR",
            type=float,
        ),
        OpenApiParameter(
            name="price_max",
            description="Maximum price in EUR",
            type=float,
        ),
        OpenApiParameter(
            name="rooms_min",
            description="Minimum number of rooms",
            type=int,
        ),
        OpenApiParameter(
            name="rooms_max",
            description="Maximum number of rooms",
            type=int,
        ),
        OpenApiParameter(
            name="property_type",
            description="Property type (apartment, house, studio, ...)",
        ),
        OpenApiParameter(
            name="amenities",
            description="Comma-separated amenity slugs (e.g. wifi,balcony)",
        ),
        OpenApiParameter(
            name="city",
            description="City name (case-insensitive)",
        ),
        OpenApiParameter(
            name="has_images",
            description="Filter listings with images: true / false",
            type=bool,
        ),
        OpenApiParameter(
            name="order_by",
            description=(
                "Ordering strategy. "
                f"Available values: {', '.join(sorted(ListingOrderBy.ALL))}"
            ),
        ),
    ],
)
class ListingPublicListView(ListAPIView):
    """
    Public listings search endpoint.
    """

    permission_classes = [AllowAny]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        params = self.request.query_params

        # Save search query for analytics (if present)
        if params.get("search") or params.get("q"):
            save_search_query(
                query=params.get("search") or params.get("q"),
                user=self.request.user,
            )

        return (
            search_listings(
                **build_search_listings_kwargs(
                    params=params,
                )
            )
            .prefetch_related("property__amenities")
            .order_by("-created_at")
        )

    def options(self, request, *args, **kwargs):
        """
        Expose available ordering strategies for frontend.
        """
        response = super().options(request, *args, **kwargs)
        response.data = response.data or {}
        response.data["order_by_choices"] = sorted(ListingOrderBy.ALL)
        return response


class ListingMyListView(ListAPIView):
    """
    Authenticated user's own listings.
    Includes listings of any status (ACTIVE / INACTIVE / DRAFT).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        return (
            search_listings(
                **build_search_listings_kwargs(
                    params=self.request.query_params,
                    owner=self.request.user,
                    include_non_active=True,
                )
            )
            .prefetch_related("property__amenities")
            .order_by("-created_at")
        )