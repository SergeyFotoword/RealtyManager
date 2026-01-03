from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_delete import ReviewDeleteSerializer


class ReviewDeleteView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewDeleteSerializer
    queryset = Review.objects.all()  # было not_removed()

    @extend_schema(
        summary="Delete review (soft delete)",
        request=ReviewDeleteSerializer,
        responses={
            200: ReviewDeleteSerializer,
            400: OpenApiResponse(description="Validation or business rule error"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Review not found"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)