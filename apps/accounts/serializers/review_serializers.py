from rest_framework import serializers

from ..models import User
from ..models.review import Review


class ReviewReadSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source="reviewer.id")

    class Meta:
        model = Review
        fields = "__all__"


class ReviewWriteSerializer(serializers.ModelSerializer):
    reviewed_user = serializers.PrimaryKeyRelatedField(
        source="target",
        queryset=User.objects.all(),
    )

    class Meta:
        model = Review
        fields = (
            "reviewed_user",
            "role",
            "score",
            "comment",
        )