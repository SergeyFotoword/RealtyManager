from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.serializers.review_create import ReviewCreateSerializer


class ReviewCreateView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]