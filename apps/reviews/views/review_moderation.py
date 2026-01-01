from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_moderation import ReviewModerationSerializer
from apps.reviews.services.review_moderation import moderate_review


class ReviewModerationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Moderate review (approve / reject / hide)",
        request=ReviewModerationSerializer,
        responses={
            200: OpenApiResponse(description="Moderation applied"),
            400: OpenApiResponse(description="Invalid action"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Review not found"),
        },
    )
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