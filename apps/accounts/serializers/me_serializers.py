from rest_framework import serializers
from apps.accounts.models.profile import UserProfile


class MeReadSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    is_staff = serializers.BooleanField(source="user.is_staff", read_only=True)
    is_superuser = serializers.BooleanField(source="user.is_superuser", read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "public_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "bio",
            "avatar_url",
            "nickname",
            "nickname_updated_at",
            "roles",
            "is_staff",
            "is_superuser",
        )

    def get_roles(self, obj: UserProfile):
        user = obj.user
        if hasattr(user, "roles"):
            return list(user.roles.values_list("name", flat=True))
        return []

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()


class MeProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "bio",
            "phone",
        )

    def update(self, instance: UserProfile, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save(update_fields=validated_data.keys())
        return instance