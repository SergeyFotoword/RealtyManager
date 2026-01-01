from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reviews.serializers.review_create import ReviewCreateSerializer


class ReviewCreateView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create review",
        request=ReviewCreateSerializer,
        responses={
            201: ReviewCreateSerializer,
            400: OpenApiResponse(description="Validation or business rule error"),
            401: OpenApiResponse(description="Unauthorized"),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)