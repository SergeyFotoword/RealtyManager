from rest_framework import serializers
from apps.listings.models import Listing, ListingStatus


class ListingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = (
            "title",
            "description",
            "price_eur",
            "status",
        )

    def validate_status(self, value):
        if value not in ListingStatus.values:
            raise serializers.ValidationError("Invalid status")
        return value