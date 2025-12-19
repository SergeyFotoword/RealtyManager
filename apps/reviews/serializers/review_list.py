from rest_framework import serializers
from apps.reviews.models.review import Review


class ReviewPublicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "rating", "comment", "language", "created_at"]


class ReviewPrivateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "comment",
            "language",
            "created_at",
            "moderation_status",
            "is_hidden",
            "direction",
            "booking_id",
            "reviewer_id",
            "target_id",
        ]