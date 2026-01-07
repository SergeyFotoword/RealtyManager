from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import PropertyType

class PropertyChoicesView(APIView):
    def get(self, request):
        return Response({
            "property_type": [
                {"value": choice.value, "label": choice.label}
                for choice in PropertyType
            ]
        })