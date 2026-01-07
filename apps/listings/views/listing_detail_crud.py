from django.utils import timezone
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.listings.models import Listing
from apps.listings.permissions import IsOwner
from apps.listings.serializers.listing_update import ListingUpdateSerializer
from apps.listings.serializers.listing_list import ListingListSerializer
from apps.listings.services.listing_view import track_listing_view


class ListingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.filter(is_deleted=False)

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsOwner()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ListingUpdateSerializer
        return ListingListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        track_listing_view(
            listing=instance,
            user=request.user,
        )

        return super().retrieve(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_at"])