from __future__ import annotations

from apps.reviews.models.review import Review, ReviewModerationStatus, ReviewDirection
from apps.reviews.models.user_rating import UserRating
from apps.reviews.models.property_rating import PropertyRating


def contributes_to_rating(review: Review) -> bool:
    """
    Whether this review should affect rating aggregates:
    - must be approved
    - must not be hidden
    - must not be removed
    """
    if review.is_hidden:
        return False
    if review.moderation_status != ReviewModerationStatus.APPROVED:
        return False
    if review.moderation_status in (
        ReviewModerationStatus.USER_REMOVED,
        ReviewModerationStatus.MODERATOR_REMOVED,
    ):
        return False
    return True


def _recalc_fields(obj) -> None:
    # Keep consistent / safe state even if something went wrong earlier
    if obj.reviews_count <= 0:
        obj.reviews_count = 0
        obj.total_score = 0
        obj.average = 0
        return

    if obj.total_score < 0:
        obj.total_score = 0

    obj.average = obj.total_score / obj.reviews_count


def apply_add(review: Review) -> None:
    """
    Adds this review into aggregates (UserRating always; PropertyRating only for TENANT->LANDLORD).
    Safe to call even if rating rows do not exist (will be created).
    """
    user_rating, _ = UserRating.objects.get_or_create(user=review.target)
    user_rating.reviews_count += 1
    user_rating.total_score += int(review.rating)
    _recalc_fields(user_rating)
    user_rating.save(update_fields=["reviews_count", "total_score", "average", "updated_at"])

    if review.direction == ReviewDirection.TENANT_TO_LANDLORD:
        # Prefer FK on review if present; otherwise resolve by booking->listing->property
        pr = None
        if review.property_rating_id:
            pr = review.property_rating
        else:
            property_obj = review.booking.listing.property
            pr, _ = PropertyRating.objects.get_or_create(property=property_obj)

        pr.reviews_count += 1
        pr.total_score += int(review.rating)
        _recalc_fields(pr)
        pr.save(update_fields=["reviews_count", "total_score", "average", "updated_at"])


def apply_remove(review: Review) -> None:
    """
    Removes this review from aggregates (inverse of apply_add).
    Clamps values to avoid negative counts/scores.
    """
    user_rating, _ = UserRating.objects.get_or_create(user=review.target)
    user_rating.reviews_count -= 1
    user_rating.total_score -= int(review.rating)
    _recalc_fields(user_rating)
    user_rating.save(update_fields=["reviews_count", "total_score", "average", "updated_at"])

    if review.direction == ReviewDirection.TENANT_TO_LANDLORD:
        pr = None
        if review.property_rating_id:
            pr = review.property_rating
        else:
            property_obj = review.booking.listing.property
            pr, _ = PropertyRating.objects.get_or_create(property=property_obj)

        pr.reviews_count -= 1
        pr.total_score -= int(review.rating)
        _recalc_fields(pr)
        pr.save(update_fields=["reviews_count", "total_score", "average", "updated_at"])