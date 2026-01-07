from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.accounts.permissions import IsLandlord
from apps.listings.serializers.listing_create import ListingCreateSerializer
from apps.listings.serializers.listing_list import ListingListSerializer
from apps.listings.services.listing_search import search_listings
from apps.listings.services.search_history import save_search_query
from apps.listings.utils.search_params import build_search_listings_kwargs


@extend_schema(
    summary="List or create listings",
    description=(
        "GET — public search & list\n"
        "POST — create listing (LANDLORD only)"
    )
)
class ListingPublicListCreateView(ListCreateAPIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsLandlord()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ListingCreateSerializer
        return ListingListSerializer

    def get_queryset(self):
        params = self.request.query_params

        if self.request.method == "GET" and (params.get("search") or params.get("q")):
            save_search_query(
                query=params.get("search") or params.get("q"),
                user=self.request.user,
            )

        return (
            search_listings(
                **build_search_listings_kwargs(params=params)
            )
            .prefetch_related("property__amenities")
            .order_by("-created_at")
        )