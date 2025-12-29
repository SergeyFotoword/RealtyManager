from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.properties.models import Amenity
from apps.properties.serializers.amenity import AmenitySerializer


class AmenityListView(ListAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Amenity.objects.filter(is_active=True).order_by("name")