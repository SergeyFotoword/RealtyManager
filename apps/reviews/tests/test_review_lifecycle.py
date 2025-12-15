from django.core.exceptions import ValidationError

from apps.reviews.services.review import create_review
from apps.reviews.tests.base import BaseReviewTest


class ReviewLifecycleTest(BaseReviewTest):

    def test_review_not_allowed_without_checkin_and_checkout(self):
        with self.assertRaises(ValidationError):
            create_review(
                booking=self.booking,
                reviewer=self.tenant,
                rating=5,
                role=self.role_landlord,
            )

    def test_review_not_allowed_with_checkin_only(self):
        self.booking.checkin_at = self.booking.created_at
        self.booking.save(update_fields=["checkin_at"])

        with self.assertRaises(ValidationError):
            create_review(
                booking=self.booking,
                reviewer=self.tenant,
                rating=5,
                role=self.role_landlord,
            )

    def test_review_allowed_after_checkout(self):
        self.complete_stay()

        review = create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_landlord,
        )

        self.assertEqual(review.target, self.landlord)