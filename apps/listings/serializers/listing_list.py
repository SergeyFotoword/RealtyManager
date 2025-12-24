from rest_framework import serializers
from apps.listings.models import Listing


class ListingListSerializer(serializers.ModelSerializer):
    property_type = serializers.CharField(
        source="property.property_type"
    )
    rooms = serializers.IntegerField(
        source="property.rooms"
    )

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "price_eur",
            "created_at",
            "property_type",
            "rooms",
        ]