from rest_framework import serializers
from ..models.user import User
from .role_serializers import RoleSerializer

class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "roles"]