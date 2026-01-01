from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema

from ..models.review import Review
from ..serializers.review_serializers import (
    ReviewReadSerializer,
    ReviewWriteSerializer,
)
from ..permissions import IsReviewerOrReadOnly


@extend_schema_view(
    list=extend_schema(summary="List reviews"),
    retrieve=extend_schema(summary="Get review"),
    create=extend_schema(summary="Create review"),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsReviewerOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReviewReadSerializer
        return ReviewWriteSerializer

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)