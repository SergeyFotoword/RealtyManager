from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.reviews.services.review_moderation import moderate_review
from apps.reviews.services.review_delete import delete_review
from apps.reviews.models.review import ReviewModerationStatus
from apps.reviews.tests.base import BaseReviewTest

class ReviewModerationTest(BaseReviewTest, TestCase):
    def test_moderator_can_remove_review(self):
        self.complete_stay()

        review = self.create_review_as_tenant()

        moderator = self.create_user(is_staff=True)

        moderate_review(
            review=review,
            moderator=moderator,
            action="remove",
        )

        review.refresh_from_db()
        assert review.moderation_status == ReviewModerationStatus.MODERATOR_REMOVED

    def test_non_moderator_cannot_moderate(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        with self.assertRaises(ValidationError):
            moderate_review(
                review=review,
                moderator=self.tenant,
                action="remove",
            )

    def test_author_can_soft_delete_own_review(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        delete_review(
            review=review,
            actor=self.tenant,
        )

        review.refresh_from_db()
        assert review.moderation_status == ReviewModerationStatus.USER_REMOVED

    def test_user_cannot_restore_review(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        delete_review(review=review, actor=self.tenant)

        with self.assertRaises(ValidationError):
            moderate_review(
                review=review,
                moderator=self.tenant,
                action="restore",
            )

    def test_moderator_can_restore_review(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        moderator = self.create_user(is_staff=True)

        moderate_review(review=review, moderator=moderator, action="remove")
        moderate_review(review=review, moderator=moderator, action="restore")

        review.refresh_from_db()
        assert review.moderation_status == ReviewModerationStatus.APPROVED

    def test_removed_review_cannot_be_edited(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        delete_review(review=review, actor=self.tenant)

        from apps.reviews.services.review_edit import edit_review

        with self.assertRaises(ValidationError):
            edit_review(
                review=review,
                editor=self.tenant,
                rating=3,
            )