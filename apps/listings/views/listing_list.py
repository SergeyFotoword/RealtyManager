from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.listings.serializers.listing_list import ListingListSerializer
from apps.listings.services.listing_search import search_listings
from apps.listings.constants import ListingOrderBy
from apps.listings.services.search_history import save_search_query

class ListingPublicListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        p = self.request.query_params
        query = p.get("search") or p.get("q")

        order_by = p.get("order_by")
        if order_by not in ListingOrderBy.ALL:
            order_by = None

        save_search_query(
            query=query,
            user=self.request.user,
        )

        return search_listings(
            query=query,
            price_min=p.get("price_min"),
            price_max=p.get("price_max"),
            rooms_min=p.get("rooms_min"),
            rooms_max=p.get("rooms_max"),
            property_type=p.get("property_type"),
            city=p.get("city"),
            has_images=(p.get("has_images") == "true") if p.get("has_images") else None,
            order_by=order_by,
        )

    def options(self, request, *args, **kwargs):
        response = super().options(request, *args, **kwargs)
        response.data = response.data or {}
        response.data["order_by_choices"] = sorted(ListingOrderBy.ALL)
        return response


class ListingMyListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListingListSerializer

    def get_queryset(self):
        p = self.request.query_params
        query = p.get("search") or p.get("q")

        order_by = p.get("order_by")
        if order_by not in ListingOrderBy.ALL:
            order_by = None

        # my: any, without deleted
        return search_listings(
            query=query,
            price_min=p.get("price_min"),
            price_max=p.get("price_max"),
            rooms_min=p.get("rooms_min"),
            rooms_max=p.get("rooms_max"),
            property_type=p.get("property_type"),
            city=p.get("city"),
            has_images=(p.get("has_images") == "true") if p.get("has_images") else None,
            order_by=order_by,
            owner=self.request.user,
            include_non_active=True,
        )