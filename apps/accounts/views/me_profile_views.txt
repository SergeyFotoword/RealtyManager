from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.accounts.models.profile import UserProfile
from apps.accounts.serializers.me_serializers import MeProfileSerializer


class MeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MeProfileSerializer,
        summary="Get my profile",
        description="Returns profile of the currently authenticated user",
    )
    def get(self, request):
        profile, _ = UserProfile.objects.select_related("user").get_or_create(user=request.user)
        return Response(MeProfileSerializer(profile).data)