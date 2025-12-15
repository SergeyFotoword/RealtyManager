from rest_framework import serializers
from ..models.review import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source="reviewer.id")

    class Meta:
        model = Review
        fields = "__all__"