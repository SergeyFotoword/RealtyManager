from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_edit import ReviewEditSerializer


class ReviewEditView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewEditSerializer

    # You can only edit "not deleted" items (soft delete via moderation_status)
    queryset = Review.objects.not_removed()