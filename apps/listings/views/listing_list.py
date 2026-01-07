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
        "- Full-text search\n"
        "- Filters by price, rooms, city, amenities\n"
        "- Ordering by price, date, popularity\n"
    ),
    parameters=[
        OpenApiParameter(name="search"),
        OpenApiParameter(name="price_min", type=float),
        OpenApiParameter(name="price_max", type=float),
        OpenApiParameter(name="rooms_min", type=int),
        OpenApiParameter(name="rooms_max", type=int),
        OpenApiParameter(name="city"),
        OpenApiParameter(name="amenities"),
        OpenApiParameter(name="has_images", type=bool),
        OpenApiParameter(
            name="order_by",
            description="Ordering strategy",
            enum=sorted(ListingOrderBy.PUBLIC),
        ),
    ],
)
class ListingPublicListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        params = self.request.query_params

        if params.get("search") or params.get("q"):
            save_search_query(
                query=params.get("search") or params.get("q"),
                user=self.request.user,
            )

        return (
            search_listings(**build_search_listings_kwargs(params=params))
            .prefetch_related("property__amenities")
        )

    def options(self, request, *args, **kwargs):
        """
        Tests expect: order_by_choices = list[str]
        """
        response = super().options(request, *args, **kwargs)
        response.data = response.data or {}

        # ВАЖНО: list[str], не dict'и
        response.data["order_by_choices"] = sorted(ListingOrderBy.ALL)
        return response


class ListingMyListView(ListAPIView):
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
        )