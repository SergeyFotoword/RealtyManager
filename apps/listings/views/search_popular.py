from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.listings.services.search_popular import(
    get_popular_search_queries,
)


class PopularSearchQueryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        period = request.query_params.get("period")

        if period == "7d":
            data = get_popular_search_queries(days=7)
        elif period == "30d":
            data = get_popular_search_queries(days=30)
        else:
            data = get_popular_search_queries()

        return Response(data)