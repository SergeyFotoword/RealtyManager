from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.bookings.models.booking import Booking
from apps.bookings.services.booking import create_booking


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
            raise ValidationError({"end_date": "End date must be after start date."})

        try:
            listing = Listing.objects.select_related("owner").get(id=attrs["listing_id"])
        except Listing.DoesNotExist:
            raise ValidationError({"listing_id": "Listing does not exist."})

        if listing.owner == request.user:
            raise ValidationError("You cannot book your own listing.")

        attrs["listing"] = listing
        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        # IMPORTANT:
        # use service so landlord/status/overlap rules are applied
        try:
            return create_booking(
                listing=validated_data["listing"],
                tenant=request.user,
                start_date=validated_data["start_date"],
                end_date=validated_data["end_date"],
            )
        except DjangoValidationError as e:
            # convert django ValidationError -> DRF ValidationError (400)
            if hasattr(e, "message_dict"):
                raise ValidationError(e.message_dict)
            if hasattr(e, "messages") and e.messages:
                raise ValidationError({"detail": e.messages[0]})
            raise ValidationError({"detail": str(e)})


class BookingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "listing_id",
            "tenant_id",
            "landlord_id",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "confirmed_at",
            "cancelled_at",
            "checkin_at",
            "checkout_at",
        ]