from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.accounts.models.profile import UserProfile
from apps.accounts.serializers.me_nickname_serializers import (
    MeNicknameSerializer,
    ChangeNicknameSerializer,
)
from apps.accounts.services.profile import change_nickname


class MeNicknameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        data = {
            "nickname": profile.nickname,
            "nickname_updated_at": profile.nickname_updated_at,
        }
        return Response(MeNicknameSerializer(data).data)

    @transaction.atomic
    def patch(self, request):
        profile = UserProfile.objects.select_for_update().get(user=request.user)

        serializer = ChangeNicknameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        expected = serializer.validated_data.get("expected_nickname_updated_at", None)
        if "expected_nickname_updated_at" in serializer.validated_data:
            expected = serializer.validated_data["expected_nickname_updated_at"]
            if expected != profile.nickname_updated_at:
                return Response(
                    {"detail": "Nickname was changed already. Refresh and try again."},
                    status=status.HTTP_409_CONFLICT,
                )

        try:
            change_nickname(profile, serializer.validated_data["nickname"])
        except DjangoValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

        profile.refresh_from_db()
        data = {
            "nickname": profile.nickname,
            "nickname_updated_at": profile.nickname_updated_at,
        }
        return Response(MeNicknameSerializer(data).data, status=status.HTTP_200_OK)