from django.apps import apps
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.listings.models import Listing, ListingStatus
from apps.listings.serializers.listing_list import ListingListSerializer

Property = apps.get_model("properties", "Property")


class ListingCreateSerializer(serializers.ModelSerializer):
    """
    Create Listing.

    - property_id (write-only) → property
    - owner -- auto
    - status = DRAFT
    - response = ListingListSerializer
    """

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

    def validate_property_id(self, property_obj):
        """
        Ownership verification.
        ACHTUNG: validate_property_id, sondern validate_property
        """
        request = self.context["request"]

        if property_obj.owner != request.user:
            raise ValidationError(
                "You can create a listing only for your own property."
            )

        return property_obj

    def create(self, validated_data):
        request = self.context["request"]

        validated_data["owner"] = request.user
        validated_data.setdefault("status", ListingStatus.DRAFT)

        return super().create(validated_data)

    def to_representation(self, instance):
        return ListingListSerializer(
            instance,
            context=self.context,
        ).data