from rest_framework import serializers
from apps.bookings.models.booking import Booking


class BookingCreateSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


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