from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.models.profile import UserProfile
from apps.accounts.serializers.me_serializers import (
    MeReadSerializer,
    MeProfileUpdateSerializer,
)
from apps.accounts.serializers.me_nickname_serializers import (
    MeNicknameReadSerializer,
    MeNicknameUpdateSerializer,
)


def get_or_create_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.select_related("user").get_or_create(user=user)
    return profile

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="Get my profile",
        responses={200: MeReadSerializer},
    )
    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(MeReadSerializer(profile).data)


class MeProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="Update my profile",
        request=MeProfileUpdateSerializer,
        responses={200: MeReadSerializer},
    )
    def patch(self, request):
        profile = get_or_create_profile(request.user)

        serializer = MeProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(MeReadSerializer(serializer.instance).data)


class MeNicknameView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="Get my nickname",
        responses={200: MeNicknameReadSerializer},
    )
    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(MeNicknameReadSerializer(profile).data)

    @extend_schema(
        tags=["accounts"],
        summary="Change my nickname",
        request=MeNicknameUpdateSerializer,
        description=(
                "For the FIRST nickname set, do NOT send expected_nickname_updated_at.\n\n"
                "Send expected_nickname_updated_at ONLY when updating an existing nickname "
                "to enable optimistic locking and prevent concurrent updates."
        ),
        responses={
            200: MeNicknameReadSerializer,
            400: OpenApiResponse(description="Validation error / nickname conflict"),
        },
    )
    def patch(self, request):
        profile = get_or_create_profile(request.user)

        serializer = MeNicknameUpdateSerializer(
            data=request.data,
            context={"profile": profile},
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(MeNicknameReadSerializer(profile).data)