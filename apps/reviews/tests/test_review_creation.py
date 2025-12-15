from django.core.exceptions import ValidationError

from apps.reviews.services.review import create_review
from apps.reviews.models.review import Review
from apps.reviews.tests.base import BaseReviewTest


class ReviewCreationTest(BaseReviewTest):

    def test_review_created_successfully(self):
        self.complete_stay()

        review = create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_landlord,
            comment="Great stay!",
        )

        self.assertIsInstance(review, Review)

    def test_cannot_create_second_review_for_same_booking(self):
        self.complete_stay()

        create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_landlord,
        )

        with self.assertRaises(ValidationError):
            create_review(
                booking=self.booking,
                reviewer=self.tenant,
                rating=4,
                role=self.role_landlord,
            )