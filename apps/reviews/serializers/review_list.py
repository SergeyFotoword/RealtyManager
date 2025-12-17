from rest_framework import serializers

from apps.reviews.models import Review


class ReviewListSerializer(serializers.ModelSerializer):
    reviewer_id = serializers.IntegerField(source="reviewer.id", read_only=True)
    target_id = serializers.IntegerField(source="target.id", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "booking_id",
            "reviewer_id",
            "target_id",
            "direction",
            "rating",
            "comment",
            "language",
            "created_at",
        ]
        read_only_fields = fields