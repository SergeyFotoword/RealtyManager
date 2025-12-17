from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.bookings.models.booking import Booking
from apps.accounts.models.role import Role
from apps.reviews.models.review import Review
from apps.reviews.services.review import create_review


class ReviewCreateSerializer(serializers.ModelSerializer):

    booking_id = serializers.PrimaryKeyRelatedField(
        source="booking",
        queryset=Booking.objects.all(),
        write_only=True,
        required=True,
    )

    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "booking_id",   # input
            "rating",
            "comment",
            "language",
            "role",
        ]
        read_only_fields = ["id"]

    def _infer_role(self, *, booking: Booking, reviewer) -> Role:

        if reviewer == booking.tenant:
            wanted = "landlord"
        elif reviewer == booking.landlord:
            wanted = "tenant"
        else:
            raise serializers.ValidationError("Reviewer must be a booking participant.")

        role = Role.objects.filter(name__iexact=wanted).first()
        if role is None:
            raise serializers.ValidationError(
                f"Role '{wanted}' not found. Create Role(name='{wanted}')."
            )
        return role

    def create(self, validated_data):
        request = self.context["request"]
        booking: Booking = validated_data["booking"]
        rating: int = validated_data["rating"]

        role = validated_data.get("role") or self._infer_role(
            booking=booking,
            reviewer=request.user,
        )

        try:
            review = create_review(
                booking=booking,
                reviewer=request.user,
                rating=rating,
                role=role,
                comment=validated_data.get("comment", ""),
                language=validated_data.get("language", ""),
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        return review