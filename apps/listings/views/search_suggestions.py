from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.listings.services.search_suggestions import get_search_suggestions


class SearchSuggestionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        prefix = request.query_params.get("q")
        data = get_search_suggestions(prefix=prefix, limit=5)
        return Response(data)