from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_list import (
    ReviewPublicListSerializer,
    ReviewPrivateListSerializer,
)


class ReviewPublicListView(ListAPIView):
    """
    Public feed: only what is visible to everyone.
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewPublicListSerializer

    def get_queryset(self):
        return Review.objects.visible_public().order_by("-created_at")


class ReviewPrivateListView(ListAPIView):
    """
    Private feed: user sees all reviews where he is reviewer or target.
    Includes removed/hidden/not-approved (owner view).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewPrivateListSerializer

    def get_queryset(self):
        user = self.request.user
        return (
            Review.objects.filter(Q(reviewer=user) | Q(target=user))
            .order_by("-created_at")
        )