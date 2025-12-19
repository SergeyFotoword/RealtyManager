from rest_framework import serializers

from apps.reviews.services.review_moderation import ACTION_MAP


class ReviewModerationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=tuple(ACTION_MAP)  # ← КЛЮЧЕВО
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )