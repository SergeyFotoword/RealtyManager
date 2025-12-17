from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.models.review import Review
from apps.reviews.serializers.review_list import ReviewListSerializer


class ReviewListView(ListAPIView):
    serializer_class = ReviewListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Review.objects.not_removed()
            .filter(Q(reviewer=user) | Q(target=user))
            .select_related("reviewer", "target")
        )