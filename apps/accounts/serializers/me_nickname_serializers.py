from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models.profile import UserProfile
from apps.accounts.services.profile import change_nickname


class MeNicknameReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("nickname", "nickname_updated_at")


class MeNicknameUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(
        max_length=64,
        allow_blank=False,
        trim_whitespace=True,
        required=True,
    )

    expected_nickname_updated_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    def validate_nickname(self, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Nickname is too short.")
        return value

    def validate(self, attrs):
        """
        Optimistic locking lives here intentionally.

        DO NOT move this logic to save():
        DRF will normalize ValidationError and drop custom error codes.
        """
        profile: UserProfile = self.context["profile"]

        expected = attrs.get("expected_nickname_updated_at")
        current = profile.nickname_updated_at


        if expected is not None and current is not None:
            if expected != current:
                pass
            else:
                raise serializers.ValidationError(
                    {
                        "nickname": serializers.ErrorDetail(
                            "Nickname was changed already. Refresh and try again.",
                            code="nickname_already_changed",
                        )
                    }
                )

        return attrs

    def save(self, **kwargs) -> UserProfile:
        profile: UserProfile = self.context["profile"]

        try:
            return change_nickname(
                profile,
                self.validated_data["nickname"],
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)