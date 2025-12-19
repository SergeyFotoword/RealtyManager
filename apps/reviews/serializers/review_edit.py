from rest_framework import serializers
from apps.reviews.services.review_edit import edit_review


class ReviewEditSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    language = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        request = self.context["request"]
        return edit_review(
            review=instance,
            editor=request.user,
            rating=validated_data.get("rating"),
            comment=validated_data.get("comment"),
            language=validated_data.get("language"),
        )