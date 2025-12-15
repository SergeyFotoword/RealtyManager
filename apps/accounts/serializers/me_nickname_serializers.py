from rest_framework import serializers

class MeNicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=32, allow_null=True)
    nickname_updated_at = serializers.DateTimeField(allow_null=True)

class ChangeNicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=32)
    expected_nickname_updated_at = serializers.DateTimeField(required=False, allow_null=True)