from rest_framework import viewsets, permissions
from ..models.review import Review
from ..serializers.review_serializers import ReviewSerializer
from ..permissions import IsReviewerOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsReviewerOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)