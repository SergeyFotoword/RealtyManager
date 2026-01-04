from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsLandlord
from apps.properties.models import Property
from apps.properties.serializers.property import PropertySerializer


@extend_schema(
    summary="Retrieve / update / delete property",
    description=(
        "Retrieve, update or delete a property owned by the current user.\n\n"
        "Deletion rules:\n"
        "- Property can be deleted ONLY if it has no listings.\n"
        "- If at least one listing exists, deletion is forbidden.\n"
    ),
)
class PropertyDetailView(RetrieveUpdateDestroyAPIView):
    """
    Property detail view.

    - Only LANDLORD
    - Only own properties
    - Deletion forbidden if property has listings
    """

    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsLandlord]

    def get_queryset(self):
        """
        Landlord sees ONLY his own properties.
        """
        return Property.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance: Property):
        """
        Business rule:
        Property with listings cannot be deleted.
        """
        if instance.listings.exists():
            raise ValidationError(
                {
                    "detail": (
                        "You cannot delete a property "
                        "that has at least one listing."
                    )
                }
            )

        instance.delete()