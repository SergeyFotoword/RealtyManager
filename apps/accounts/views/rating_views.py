from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.rating import Rating
from ..serializers.rating_serializers import RatingSerializer
from rest_framework.permissions import IsAuthenticated

class UserRatingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        ratings = Rating.objects.filter(user_id=user_id).select_related("role")
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)