from django.core.exceptions import ValidationError

from apps.reviews.models.review import Review, ReviewModerationStatus
from apps.reviews.models.review_audit import ReviewAudit, ReviewAuditAction


def _is_moderator(user) -> bool:
    return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))


DELETE_MAP = {
    "user": (
        ReviewModerationStatus.USER_REMOVED,
        ReviewAuditAction.USER_REMOVED,
    ),
    "moderator": (
        ReviewModerationStatus.MODERATOR_REMOVED,
        ReviewAuditAction.MODERATOR_REMOVED,
    ),
}


def delete_review(*, review: Review, actor) -> Review:
    """
    Soft delete:
      - author -> USER_REMOVED
      - staff/superuser -> MODERATOR_REMOVED
    Also writes ReviewAudit with from_status/to_status.
    """

    if actor == review.reviewer:
        new_status, audit_action = DELETE_MAP["user"]
    elif _is_moderator(actor):
        new_status, audit_action = DELETE_MAP["moderator"]
    else:
        raise ValidationError("You do not have permission to delete this review.")

    from_status = review.moderation_status
    review.moderation_status = new_status
    review.save(update_fields=["moderation_status"])

    ReviewAudit.objects.create(
        review=review,
        actor=actor,
        action=audit_action,
        from_status=from_status,
        to_status=new_status,
    )

    return review