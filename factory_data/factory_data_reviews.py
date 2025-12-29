from __future__ import annotations

import random
from django.db import transaction

from apps.reviews.models.review import (
    Review,
    ReviewDirection,
    ReviewModerationStatus,
)
from apps.reviews.models.review_audit import (
    ReviewAudit,
    ReviewAuditAction,
)
from apps.reviews.models.property_rating import PropertyRating
from apps.reviews.models.user_rating import UserRating

from apps.bookings.models.booking import Booking, BookingStatus
from apps.accounts.models.role import Role

from ._pool import make_picker


# ---------- helpers ----------

def _random_rating() -> int:
    return random.choices(
        [1, 2, 3, 4, 5],
        weights=[3, 7, 25, 40, 25],
        k=1,
    )[0]


COMMENTS_POSITIVE = [
    "Everything was great, would definitely recommend.",
    "Excellent experience, no issues at all.",
    "Very friendly and professional.",
]

COMMENTS_NEUTRAL = [
    "Overall okay, nothing special.",
    "Mostly fine, a few minor issues.",
]

COMMENTS_NEGATIVE = [
    "Not satisfied with the experience.",
    "There were several problems.",
]


def _random_comment(score: int) -> str:
    if score >= 4:
        return random.choice(COMMENTS_POSITIVE)
    if score == 3:
        return random.choice(COMMENTS_NEUTRAL)
    return random.choice(COMMENTS_NEGATIVE)


# ---------- pickers ----------

pick_completed_booking = make_picker(
    lambda: Booking.objects.filter(
        status=BookingStatus.COMPLETED,
        checkin_at__isnull=False,
        checkout_at__isnull=False,
    ),
    what="completed bookings",
)


# ---------- core creators ----------

def _get_or_create_property_rating(booking: Booking) -> PropertyRating:
    property_obj = booking.listing.property
    rating, _ = PropertyRating.objects.get_or_create(property=property_obj)
    return rating


def _get_or_create_user_rating(user) -> UserRating:
    rating, _ = UserRating.objects.get_or_create(user=user)
    return rating


def _create_review(
    *,
    booking: Booking,
    reviewer,
    target,
    direction: str,
    role: Role,
    property_rating: PropertyRating | None,
) -> Review:
    score = _random_rating()
    comment = _random_comment(score)

    review = Review.objects.create(
        booking=booking,
        reviewer=reviewer,
        target=target,
        direction=direction,
        role=role,
        rating=score,
        property_rating=property_rating,
        comment=comment,
        language="en",
        moderation_status=ReviewModerationStatus.APPROVED,
        is_hidden=False,
    )

    # audit log (MANDATORY)
    ReviewAudit.objects.create(
        review=review,
        actor=reviewer,
        action=ReviewAuditAction.CREATED,
        from_status=None,
        to_status=ReviewModerationStatus.APPROVED,
    )

    return review


# ---------- runner ----------

@transaction.atomic
def run() -> None:
    """
    Creates:
    - tenant → landlord reviews (with PropertyRating)
    - landlord → tenant reviews (without PropertyRating)
    - recalculates PropertyRating and UserRating
    """

    print("Creating reviews…")

    bookings = list(
        Booking.objects.filter(status=BookingStatus.COMPLETED)
    )
    if not bookings:
        raise RuntimeError("No completed bookings available for reviews.")

    for booking in bookings:
        tenant = booking.tenant
        landlord = booking.landlord

        tenant_role = Role.objects.get(name="TENANT")
        landlord_role = Role.objects.get(name="LANDLORD")

        # ---------- tenant → landlord ----------
        if not Review.objects.filter(
            booking=booking,
            direction=ReviewDirection.TENANT_TO_LANDLORD,
        ).exists():

            property_rating = _get_or_create_property_rating(booking)
            review = _create_review(
                booking=booking,
                reviewer=tenant,
                target=landlord,
                direction=ReviewDirection.TENANT_TO_LANDLORD,
                role=landlord_role,
                property_rating=property_rating,
            )

            property_rating.recalculate(new_score=review.rating)

            user_rating = _get_or_create_user_rating(landlord)
            user_rating.recalculate(new_score=review.rating)

        # ---------- landlord → tenant ----------
        if not Review.objects.filter(
            booking=booking,
            direction=ReviewDirection.LANDLORD_TO_TENANT,
        ).exists():

            review = _create_review(
                booking=booking,
                reviewer=landlord,
                target=tenant,
                direction=ReviewDirection.LANDLORD_TO_TENANT,
                role=tenant_role,
                property_rating=None,
            )

            user_rating = _get_or_create_user_rating(tenant)
            user_rating.recalculate(new_score=review.rating)

    print(f"Reviews generated for {len(bookings)} bookings")