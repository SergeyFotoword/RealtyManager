from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.reviews.models.review import ReviewModerationStatus
from apps.reviews.services.review_moderation import moderate_review
from apps.reviews.services.review_delete import delete_review
from apps.reviews.tests.base import BaseReviewTest


class RatingVisibilityTransitionsTest(BaseReviewTest, TestCase):
    def test_delete_removes_contribution_from_user_and_property_rating(self):
        self.complete_stay()
        review = self.create_review_as_tenant()  # tenant -> landlord (affects property)

        # before delete
        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()

        assert self.landlord.rating.reviews_count == 1
        assert self.landlord.rating.total_score == review.rating
        assert self.landlord.rating.average == review.rating

        assert self.property.rating.reviews_count == 1
        assert self.property.rating.total_score == review.rating
        assert self.property.rating.average == review.rating

        delete_review(review=review, actor=self.tenant)

        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()

        assert self.landlord.rating.reviews_count == 0
        assert self.landlord.rating.total_score == 0
        assert self.landlord.rating.average == 0

        assert self.property.rating.reviews_count == 0
        assert self.property.rating.total_score == 0
        assert self.property.rating.average == 0

    def test_hide_unhide_updates_rating(self):
        self.complete_stay()
        review = self.create_review_as_tenant()
        moderator = self.create_user(is_staff=True)

        # hide => remove contribution
        moderate_review(review=review, moderator=moderator, action="hide")
        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()

        assert self.landlord.rating.reviews_count == 0
        assert self.landlord.rating.total_score == 0
        assert self.landlord.rating.average == 0

        assert self.property.rating.reviews_count == 0
        assert self.property.rating.total_score == 0
        assert self.property.rating.average == 0

        # unhide => add back contribution (review is still APPROVED)
        moderate_review(review=review, moderator=moderator, action="unhide")
        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()

        assert self.landlord.rating.reviews_count == 1
        assert self.landlord.rating.total_score == review.rating
        assert self.landlord.rating.average == review.rating

        assert self.property.rating.reviews_count == 1
        assert self.property.rating.total_score == review.rating
        assert self.property.rating.average == review.rating

    def test_remove_restore_updates_rating(self):
        self.complete_stay()
        review = self.create_review_as_tenant()
        moderator = self.create_user(is_staff=True)

        # remove => removed from rating
        moderate_review(review=review, moderator=moderator, action="remove")
        review.refresh_from_db()
        assert review.moderation_status == ReviewModerationStatus.MODERATOR_REMOVED

        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()
        assert self.landlord.rating.reviews_count == 0
        assert self.property.rating.reviews_count == 0

        # restore => back to approved => back in rating
        moderate_review(review=review, moderator=moderator, action="restore")
        review.refresh_from_db()
        assert review.moderation_status == ReviewModerationStatus.APPROVED

        self.landlord.rating.refresh_from_db()
        self.property.rating.refresh_from_db()
        assert self.landlord.rating.reviews_count == 1
        assert self.property.rating.reviews_count == 1

    def test_non_moderator_still_cannot_moderate(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        with self.assertRaises(ValidationError):
            moderate_review(review=review, moderator=self.tenant, action="hide")