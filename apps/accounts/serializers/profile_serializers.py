from rest_framework import serializers
from ..models.profile import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "avatar_url", "bio"]

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()