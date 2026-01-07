from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.accounts.permissions import IsLandlord
from apps.properties.models import Property
from apps.properties.serializers.property import (
    PropertySerializer,
    PropertyCreateSerializer,
)


class PropertyListCreateView(ListCreateAPIView):
    """
    GET  /api/properties/ → list of landlord's properties
    POST /api/properties/ → create property (LANDLORD only)

    IMPORTANT DRF RULE:
    - POST uses PropertyCreateSerializer for input
    - RESPONSE uses PropertySerializer
    """

    permission_classes = [IsLandlord]

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PropertyCreateSerializer
        return PropertySerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to return READ serializer in response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_obj = serializer.save()

        read_serializer = PropertySerializer(
            property_obj,
            context={"request": request},
        )

        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
        )