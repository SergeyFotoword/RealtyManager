from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_edit import ReviewEditSerializer


class ReviewEditView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewEditSerializer
    queryset = Review.objects.not_removed()

    @extend_schema(
        summary="Edit review",
        request=ReviewEditSerializer,
        responses={
            200: ReviewEditSerializer,
            400: OpenApiResponse(description="Validation or business rule error"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Review not found"),
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)