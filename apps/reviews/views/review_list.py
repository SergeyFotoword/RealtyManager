from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from drf_spectacular.utils import extend_schema

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_list import (
    ReviewPublicListSerializer,
    ReviewPrivateListSerializer,
)


@extend_schema(
    summary="Public reviews list",
    responses=ReviewPublicListSerializer(many=True),
)
class ReviewPublicListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReviewPublicListSerializer

    def get_queryset(self):
        return Review.objects.visible_public().order_by("-created_at")


@extend_schema(
    summary="My reviews list (private)",
    responses=ReviewPrivateListSerializer(many=True),
)
class ReviewPrivateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewPrivateListSerializer

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(
            Q(reviewer=user) | Q(target=user)
        ).order_by("-created_at")