from drf_spectacular.utils import extend_schema
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.listings.models import Listing
from apps.listings.permissions import IsOwner
from apps.listings.serializers.listing_update import ListingUpdateSerializer
from apps.listings.serializers.listing_list import ListingListSerializer


@extend_schema(
    summary="Update listing",
    description=(
        "Update an existing listing.\n\n"
        "- Only owner can update\n"
        "- Deleted listings cannot be updated\n"
        "- Status can be switched between ACTIVE / INACTIVE\n"
    ),
    request=ListingUpdateSerializer,
    responses={
        200: ListingListSerializer,
        401: None,
        403: None,
        404: None,
    },
)
class ListingUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ListingUpdateSerializer

    def get_queryset(self):
        return Listing.objects.filter(is_deleted=False)