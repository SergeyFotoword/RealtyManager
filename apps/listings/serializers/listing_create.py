from django.apps import apps
from rest_framework import serializers

from apps.listings.models import Listing, ListingStatus
from apps.listings.serializers.listing_list import ListingListSerializer


Property = apps.get_model("properties", "Property")


class ListingCreateSerializer(serializers.ModelSerializer):

    property_id = serializers.PrimaryKeyRelatedField(
        source="property",
        queryset=Property.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Listing
        fields = (
            "id",
            "property_id",
            "title",
            "description",
            "price_eur",
        )

    def create(self, validated_data):
        request = self.context["request"]

        validated_data["owner"] = request.user
        validated_data.setdefault("status", ListingStatus.DRAFT)

        return super().create(validated_data)

    def to_representation(self, instance):
        return ListingListSerializer(instance, context=self.context).data