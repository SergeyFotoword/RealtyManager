from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.reviews.models.review import Review
from apps.reviews.models.review_audit import ReviewAudit
from apps.reviews.serializers.review_audit import ReviewAuditSerializer


@extend_schema(
    summary="Review audit log",
    responses={
        200: ReviewAuditSerializer(many=True),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
        404: OpenApiResponse(description="Review not found"),
    },
)
class ReviewAuditView(ListAPIView):
    serializer_class = ReviewAuditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_review(self) -> Review:
        return get_object_or_404(Review, pk=self.kwargs["pk"])

    def check_permissions_for_review(self, *, review: Review) -> None:
        user = self.request.user
        is_moderator = bool(user.is_staff or user.is_superuser)
        is_participant = user.id in (review.reviewer_id, review.target_id)

        if not (is_moderator or is_participant):
            raise PermissionDenied(
                "You do not have permission to view audit logs for this review."
            )

    def get_queryset(self):
        review = self.get_review()
        self.check_permissions_for_review(review=review)
        return ReviewAudit.objects.filter(review=review).order_by("-created_at")