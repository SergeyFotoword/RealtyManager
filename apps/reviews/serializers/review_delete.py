from rest_framework import serializers
from apps.reviews.services.review_delete import delete_review
from apps.reviews.models.review import Review


class ReviewDeleteSerializer(serializers.Serializer):
    def update(self, instance: Review, validated_data):
        request = self.context["request"]
        return delete_review(review=instance, actor=request.user)