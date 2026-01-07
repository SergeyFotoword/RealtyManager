from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.role import Role
from ..serializers.role_serializers import RoleSerializer
# from ..services.role_service import add_role_to_user, remove_role_from_user
from ..services.role import add_role_to_user, remove_role_from_user

class RoleListView(generics.ListAPIView):
    """
    GET /api/accounts/roles/
    Returns available roles (dictionary endpoint).
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]


class MeBecomeLandlordView(APIView):
    """
    POST /api/accounts/become-landlord/
    Adds LANDLORD role to current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        add_role_to_user(user=request.user, role_name="LANDLORD")
        request.user.refresh_from_db()
        return Response(
            {"detail": "You are now a landlord."},
            status=status.HTTP_200_OK,
        )


class MeDropLandlordView(APIView):
    """
    POST /api/accounts/drop-landlord/
    Removes LANDLORD role from current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        remove_role_from_user(user=request.user, role_name="LANDLORD")
        return Response(
            {"detail": "Landlord role removed."},
            status=status.HTTP_200_OK,
        )