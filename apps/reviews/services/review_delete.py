from django.core.exceptions import ValidationError

from apps.reviews.models.review import Review, ReviewModerationStatus


def delete_review(*, review: Review, actor) -> Review:
    # The author (user_removed) or the moderator/admin (moderator_removed) can delete
    if actor == review.reviewer:
        review.moderation_status = ReviewModerationStatus.USER_REMOVED
        review.save(update_fields=["moderation_status"])
        return review

    # если у тебя нет ролей/permissions — оставь is_staff/is_superuser
    if getattr(actor, "is_staff", False) or getattr(actor, "is_superuser", False):
        review.moderation_status = ReviewModerationStatus.MODERATOR_REMOVED
        review.save(update_fields=["moderation_status"])
        return review

    raise ValidationError("You do not have permission to delete this review.")