from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models.profile import UserProfile
from apps.accounts.services.registration import register_user

User = get_user_model()


class RegisterRequestSerializer(serializers.Serializer):
    """
    Input per TZ:
    - name, email, password
    We also support:
    - password2 (confirmation)
    - username (optional; defaults to email)
    """
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        name = validated_data.get("name", "")
        email = validated_data["email"]
        username = validated_data.get("username") or None
        password = validated_data["password"]

        result = register_user(
            email=email,
            password=password,
            name=name,
            username=username,
            default_role="tenant",
        )
        return result


class RegisterResponseSerializer(serializers.Serializer):
    """
    Output:
    - user basic fields
    - profile public_id (useful for UI links)
    - JWT access/refresh (so Postman can immediately continue сценарий)
    """
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)

    profile_public_id = serializers.UUIDField()
    access = serializers.CharField()
    refresh = serializers.CharField()


def build_register_response(*, user: User, profile: UserProfile) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "profile_public_id": profile.public_id,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }