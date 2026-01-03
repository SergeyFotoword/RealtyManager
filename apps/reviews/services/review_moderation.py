from django.core.exceptions import ValidationError

from apps.reviews.models.review import Review, ReviewModerationStatus
from apps.reviews.models.review_audit import ReviewAudit, ReviewAuditAction
from apps.reviews.services.rating_aggregate import contributes_to_rating, apply_add, apply_remove


ACTION_MAP = {
    "remove": (
        ReviewModerationStatus.MODERATOR_REMOVED,
        ReviewAuditAction.MODERATOR_REMOVED,
        None,
    ),
    "restore": (
        ReviewModerationStatus.APPROVED,
        ReviewAuditAction.MODERATOR_RESTORED,
        None,
    ),
    "hide": (
        None,
        ReviewAuditAction.MODERATOR_HIDDEN,
        True,
    ),
    "unhide": (
        None,
        ReviewAuditAction.MODERATOR_UNHIDDEN,
        False,
    ),
}


def moderate_review(*, review: Review, moderator, action: str, reason: str = "") -> Review:
    if not (getattr(moderator, "is_staff", False) or getattr(moderator, "is_superuser", False)):
        raise ValidationError("Moderator permissions required.")

    was_contributing = contributes_to_rating(review)

    try:
        new_status, audit_action, hidden = ACTION_MAP[action]
    except KeyError:
        raise ValidationError("Unknown moderation action.")

    from_status = review.moderation_status
    to_status = from_status  # default if moderation_status not changed

    update_fields: list[str] = []

    if new_status is not None and new_status != review.moderation_status:
        review.moderation_status = new_status
        to_status = new_status
        update_fields.append("moderation_status")

    if hidden is not None and hidden != review.is_hidden:
        review.is_hidden = hidden
        update_fields.append("is_hidden")

    if update_fields:
        review.save(update_fields=update_fields)

    now_contributing = contributes_to_rating(review)

    # rating aggregates transition
    if was_contributing and not now_contributing:
        apply_remove(review)
    elif not was_contributing and now_contributing:
        apply_add(review)

    ReviewAudit.objects.create(
        review=review,
        actor=moderator,
        action=audit_action,
        from_status=from_status,
        to_status=to_status,
        reason=reason or "",
    )

    return review