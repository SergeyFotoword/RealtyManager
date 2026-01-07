from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.serializers.auth_serializers import (
    RegisterRequestSerializer,
    RegisterResponseSerializer,
    build_register_response,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        summary="Register new user (returns JWT tokens)",
        request=RegisterRequestSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()  # RegistrationResult(user, profile)
        payload = build_register_response(user=result.user, profile=result.profile)

        return Response(payload, status=status.HTTP_201_CREATED)