from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.reviews.models.review import Review, ReviewDirection, ReviewModerationStatus
from apps.reviews.models.review_audit import ReviewAudit, ReviewAuditAction

EDIT_WINDOW_MINUTES = 30


def edit_review(
    *,
    review: Review,
    editor,
    rating: int | None = None,
    comment: str | None = None,
    language: str | None = None,
) -> Review:

    if review.reviewer_id != editor.id:
        raise ValidationError("You can edit only your own review.")

    if review.moderation_status in (
        ReviewModerationStatus.USER_REMOVED,
        ReviewModerationStatus.MODERATOR_REMOVED,
    ):
        raise ValidationError("You cannot edit a removed review.")

    if timezone.now() > review.created_at + timezone.timedelta(minutes=EDIT_WINDOW_MINUTES):
        raise ValidationError("Edit window has expired.")

    if rating is not None and rating != review.rating:
        delta = rating - review.rating
        review.rating = rating

        # UserRating
        user_rating = review.target.rating
        user_rating.total_score += delta
        user_rating.average = user_rating.total_score / user_rating.reviews_count
        user_rating.save(update_fields=["total_score", "average"])

        # PropertyRating — only TENANT → LANDLORD
        if review.direction == ReviewDirection.TENANT_TO_LANDLORD:
            pr = review.property_rating
            pr.total_score += delta
            pr.average = pr.total_score / pr.reviews_count
            pr.save(update_fields=["total_score", "average"])

    if comment is not None:
        review.comment = comment

    if language is not None:
        review.language = language

    review.save(update_fields=["rating", "comment", "language"])

    ReviewAudit.objects.create(
        review=review,
        actor=editor,
        action=ReviewAuditAction.EDITED,
    )

    return review