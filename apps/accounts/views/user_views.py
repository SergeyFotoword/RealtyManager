from rest_framework import generics, permissions
from ..models.user import User
from ..serializers.user_serializers import UserSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]