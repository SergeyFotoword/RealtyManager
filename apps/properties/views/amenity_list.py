from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.properties.models import Amenity
from apps.properties.serializers.amenity import AmenitySerializer

@method_decorator(cache_page(60 * 60), name="dispatch")
class AmenityListView(ListAPIView):
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Amenity.objects.filter(is_active=True).order_by("name")