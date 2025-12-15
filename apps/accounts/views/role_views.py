from rest_framework import generics, permissions
from ..models.role import Role
from ..serializers.role_serializers import RoleSerializer


class RoleListView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]