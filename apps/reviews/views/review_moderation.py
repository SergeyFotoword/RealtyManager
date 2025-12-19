from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_moderation import ReviewModerationSerializer
from apps.reviews.services.review_moderation import moderate_review


class ReviewModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = ReviewModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = get_object_or_404(Review, pk=pk)

        moderate_review(
            review=review,
            moderator=request.user,
            action=serializer.validated_data["action"],
            reason=serializer.validated_data.get("reason", ""),
        )

        return Response(status=status.HTTP_200_OK)