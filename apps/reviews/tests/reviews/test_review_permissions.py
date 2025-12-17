from django.core.exceptions import ValidationError

from apps.reviews.services.review import create_review
from apps.reviews.tests.base import BaseReviewTest
from apps.accounts.models.user import User


class ReviewPermissionsTest(BaseReviewTest):

    def test_non_participant_cannot_leave_review(self):
        stranger = User.objects.create_user(username="stranger", password="pass")
        self.complete_stay()

        with self.assertRaises(ValidationError):
            create_review(
                booking=self.booking,
                reviewer=stranger,
                rating=5,
                role=self.role_landlord,
            )

    def test_landlord_can_review_tenant(self):
        self.complete_stay()

        review = create_review(
            booking=self.booking,
            reviewer=self.landlord,
            rating=4,
            role=self.role_tenant,
        )

        self.assertEqual(review.target, self.tenant)

        