from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.reviews.models.review import Review, ReviewDirection


EDIT_WINDOW_MINUTES = 30


def edit_review(
    *,
    review: Review,
    editor,
    rating: int | None = None,
    comment: str | None = None,
):

    if review.reviewer != editor:
        raise ValidationError("You can edit only your own review.")

    if timezone.now() > review.created_at + timezone.timedelta(minutes=EDIT_WINDOW_MINUTES):
        raise ValidationError("Edit window has expired.")

    # immutable fields protection
    if rating is not None:
        delta = rating - review.rating
        review.rating = rating

        # UserRating allways
        review.target.rating.reviews_count
        review.target.rating.total_score += delta
        review.target.rating.average = (
            review.target.rating.total_score / review.target.rating.reviews_count
        )
        review.target.rating.save(
            update_fields=["total_score", "average", "updated_at"]
        )

        # PropertyRating — only for TENANT→LANDLORD
        if review.direction == ReviewDirection.TENANT_TO_LANDLORD:
            pr = review.property_rating
            pr.total_score += delta
            pr.average = pr.total_score / pr.reviews_count
            pr.save(update_fields=["total_score", "average", "updated_at"])

    if comment is not None:
        review.comment = comment

    review.save(update_fields=["rating", "comment", "updated_at"])
    return review