from rest_framework import serializers

from apps.properties.models import Property
from apps.locations.services.location_factory import get_or_create_location


class PropertySerializer(serializers.ModelSerializer):
    """
    READ serializer for Property.
    Used for list / retrieve.
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



class PropertyCreateSerializer(serializers.ModelSerializer):
    """
    CREATE serializer for Property.

    RULES:
    - Location is canonical (service layer)
    - ManyToMany fields MUST be set after instance creation
    """

    # address fields
    state = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    street = serializers.CharField(required=False, allow_blank=True)
    house_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Property
        fields = [
            # property
            "property_type",
            "rooms",
            "area_sqm",
            "floor",
            "total_floors",
            "amenities",

            # address
            "state",
            "city",
            "postal_code",
            "street",
            "house_number",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        # 1. Extract M2M BEFORE create
        amenities = validated_data.pop("amenities", [])

        # 2. Resolve Location via service
        location = get_or_create_location(
            country="DE",
            state=validated_data.pop("state"),
            city=validated_data.pop("city"),
            postal_code=validated_data.pop("postal_code"),
            street=validated_data.pop("street", ""),
            house_number=validated_data.pop("house_number", ""),
        )

        # 3. Create Property WITHOUT M2M
        property_obj = Property.objects.create(
            owner=request.user,
            location=location,
            **validated_data,
        )

        # 4. Set M2M safely
        if amenities:
            property_obj.amenities.set(amenities)

        return property_obj
