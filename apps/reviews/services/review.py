from django.core.exceptions import ValidationError
from apps.reviews.models.rating import Rating
from apps.reviews.models.review import Review, ReviewDirection

def apply_review_to_rating(*, target, score: int):
    rating, _ = Rating.objects.get_or_create(user=target)
    rating.recalculate(new_score=score)

def create_review(
    *,
    booking,
    reviewer,
    rating: int,
    role,
    comment: str = "",
    language: str = "",
):

    if not booking.can_leave_review:
        raise ValidationError(
            "You can leave a review only after check-in and check-out."
        )

    if reviewer not in (booking.tenant, booking.landlord):
        raise ValidationError(
            "Reviewer must be a booking participant."
        )

    if reviewer == booking.tenant:
        direction = ReviewDirection.TENANT_TO_LANDLORD
        target = booking.landlord
    else:
        direction = ReviewDirection.LANDLORD_TO_TENANT
        target = booking.tenant

    if Review.objects.filter(booking=booking, direction=direction).exists():
        raise ValidationError(
            "Review for this booking and direction already exists."
        )

    review = Review.objects.create(
        booking=booking,
        reviewer=reviewer,
        target=target,
        direction=direction,
        role=role,
        rating=rating,
        comment=comment,
        language=language,
    )

    apply_review_to_rating(target=target, score=rating)
    return review

