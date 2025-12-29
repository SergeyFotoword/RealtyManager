from rest_framework import serializers
from apps.properties.models import Amenity


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "slug"]