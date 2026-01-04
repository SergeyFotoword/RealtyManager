from rest_framework import serializers

from apps.properties.models import Property


class PropertySerializer(serializers.ModelSerializer):
    """
    Universal serializer for Property:
    - create / list / retrieve / update
    - owner is always taken from request.user
    """

    class Meta:
        model = Property
        fields = [
            "id",
            "property_type",
            "rooms",
            "area_sqm",
            "floor",
            "total_floors",
            "location",
            "amenities",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        The owner is assigned automatically.
        The client CANNOT transfer the owner.
        """
        request = self.context.get("request")
        validated_data["owner"] = request.user
        return super().create(validated_data)