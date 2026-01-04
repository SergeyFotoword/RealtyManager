from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.listings.models import Listing
from apps.listings.permissions import IsOwner


@extend_schema(
    summary="Delete listing",
    description=(
        "Soft delete a listing.\n\n"
        "- Only owner can delete\n"
        "- Listing is not removed from DB\n"
        "- Deleted listing is hidden from public API\n"
    ),
    responses={
        204: None,
        401: None,
        403: None,
        404: None,
    },
)
class ListingDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Listing.objects.filter(is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_at"])