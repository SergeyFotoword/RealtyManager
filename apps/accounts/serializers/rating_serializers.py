from rest_framework import serializers
from ..models.rating import Rating

class RatingSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name")

    class Meta:
        model = Rating
        fields = ["role", "value", "reviews_count"]