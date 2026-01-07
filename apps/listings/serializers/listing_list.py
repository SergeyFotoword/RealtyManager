from rest_framework import serializers

from apps.listings.models import Listing


class ListingListSerializer(serializers.Serializer):
    """
    Read-only LIST / SEARCH serializer for listings.

    IMPORTANT:
    - This is NOT a ModelSerializer
    - It is a projection (API contract)
    - All fields are explicitly declared
    """

    class Meta:
        # drf-spectacular needs this for relation fields (SlugRelatedField, etc.)
        model = Listing
        ref_name = "ListingList"

    id = serializers.IntegerField()
    title = serializers.CharField()
    price_eur = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()

    # from Property
    property_type = serializers.CharField(source="property.property_type")
    rooms = serializers.IntegerField(source="property.rooms")

    # from Location
    city = serializers.CharField(source="property.location.city")
    state = serializers.CharField(source="property.location.state")

    # from Property (M2M)
    amenities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="slug",
        source="property.amenities",
    )
