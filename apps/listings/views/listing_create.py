from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsLandlord
from apps.listings.serializers.listing_create import ListingCreateSerializer
from apps.listings.serializers.listing_list import ListingListSerializer


@extend_schema(
    summary="Create listing",
    description=(
        "Create a new real estate listing.\n\n"
        "- Owner is set automatically\n"
        "- Listing is created with DRAFT status\n"
        "- Only LANDLORD can create listings\n"
    ),
    request=ListingCreateSerializer,
    responses={
        201: ListingListSerializer,
        401: None,
        403: None,
    },
)
class ListingCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsLandlord]
    serializer_class = ListingCreateSerializer