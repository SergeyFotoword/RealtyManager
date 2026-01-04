from django.apps import apps
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.bookings.models.booking import Booking


Listing = apps.get_model("listings", "Listing")


class BookingCreateSerializer(serializers.Serializer):
    """
    Creating a Booking.

    Rules:
    - Tenant-only (checked in view)
    - You cannot reserve your own listing
    - start_date < end_date
    """

    listing_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        request = self.context["request"]

        if attrs["start_date"] >= attrs["end_date"]:
            raise ValidationError(
                {"end_date": "End date must be after start date."}
            )

        try:
            listing = Listing.objects.select_related("owner").get(
                id=attrs["listing_id"]
            )
        except Listing.DoesNotExist:
            raise ValidationError(
                {"listing_id": "Listing does not exist."}
            )

        if listing.owner == request.user:
            raise ValidationError(
                "You cannot book your own listing."
            )

        attrs["listing"] = listing
        return attrs

    def create(self, validated_data):

        request = self.context["request"]

        return Booking.objects.create(
            listing=validated_data["listing"],
            tenant=request.user,
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
        )


class BookingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = [
            "id",
            "listing",
            "start_date",
            "end_date",
            "status",
            "created_at",
        ]