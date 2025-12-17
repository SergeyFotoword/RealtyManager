from django.core.exceptions import ValidationError

from apps.accounts.models import Role
from apps.reviews.models import Review, PropertyRating, UserRating
from apps.reviews.models.review import ReviewDirection


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
        raise ValidationError("You can leave a review only after check-in and check-out.")

    if reviewer not in (booking.tenant, booking.landlord):
        raise ValidationError("Reviewer must be a booking participant.")

    if reviewer == booking.tenant:
        direction = ReviewDirection.TENANT_TO_LANDLORD
        target = booking.landlord
        affects_property = True
    else:
        direction = ReviewDirection.LANDLORD_TO_TENANT
        target = booking.tenant
        affects_property = False

    if Review.objects.filter(booking=booking, direction=direction).exists():
        raise ValidationError(
            "Review for this booking and direction already exists."
        )

    target_rating, _ = UserRating.objects.get_or_create(user=target)

    property_rating = None
    if affects_property:
        property_obj = booking.listing.property
        property_rating, _ = PropertyRating.objects.get_or_create(
            property=property_obj
        )

    review = Review.objects.create(
        booking=booking,
        reviewer=reviewer,
        target=target,
        direction=direction,
        role=role,
        rating=rating,
        property_rating=property_rating,
        comment=comment,
        language=language,
    )

    target_rating.recalculate(new_score=rating)
    if affects_property:
        property_rating.recalculate(new_score=rating)

    return review