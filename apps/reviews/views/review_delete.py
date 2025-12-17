from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_delete import ReviewDeleteSerializer


class ReviewDeleteView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewDeleteSerializer
    queryset = Review.objects.not_removed()