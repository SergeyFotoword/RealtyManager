from rest_framework.generics import ListCreateAPIView

from apps.accounts.permissions import IsLandlord
from apps.properties.models import Property
from apps.properties.serializers.property import PropertySerializer


class PropertyListCreateView(ListCreateAPIView):
    """
    GET  /api/properties/      → list of your Property
    POST /api/properties/      → create Property (only LANDLORD)
    """

    serializer_class = PropertySerializer
    permission_classes = [IsLandlord]

    def get_queryset(self):
        """
        Landlord sees ONLY his own properties.
        """
        return Property.objects.filter(owner=self.request.user)