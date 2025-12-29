from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.listings.models import Listing
from apps.listings.serializers.listing_list import ListingListSerializer
from apps.listings.services.listing_view import track_listing_view


class ListingPublicDetailView(RetrieveAPIView):
    queryset = (
        Listing.objects
        .filter(is_deleted=False)
        .select_related("property", "property__location")
        .prefetch_related("property__amenities")
    )
    serializer_class = ListingListSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        track_listing_view(
            listing=instance,
            user=request.user,
        )

        return super().retrieve(request, *args, **kwargs)