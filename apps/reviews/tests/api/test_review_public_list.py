from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.reviews.tests.base import BaseReviewTest
from apps.reviews.models.review import ReviewModerationStatus

class ReviewPublicListTest(BaseReviewTest, APITestCase):
    def test_public_list_shows_approved_review(self):
        self.complete_stay()

        review = self.create_review_as_tenant()
        review.moderation_status = ReviewModerationStatus.APPROVED
        review.is_hidden = False
        review.save()

        url = reverse("review-list-public")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == review.id

    def test_public_list_hides_user_removed_review(self):
        self.complete_stay()

        review = self.create_review_as_tenant()
        review.moderation_status = ReviewModerationStatus.USER_REMOVED
        review.save()

        response = self.client.get(reverse("review-list-public"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_public_list_hides_moderator_removed_review(self):
        self.complete_stay()

        review = self.create_review_as_tenant()
        review.moderation_status = ReviewModerationStatus.MODERATOR_REMOVED
        review.save()

        response = self.client.get(reverse("review-list-public"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_public_list_hides_hidden_review(self):
        self.complete_stay()

        review = self.create_review_as_tenant()
        review.is_hidden = True
        review.save()

        response = self.client.get(reverse("review-list-public"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []


    def test_public_list_hides_not_approved_reviews(self):
        self.complete_stay()

        review = self.create_review_as_tenant()
        review.moderation_status = ReviewModerationStatus.PENDING
        review.save()

        response = self.client.get(reverse("review-list-public"))
        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

        review.moderation_status = ReviewModerationStatus.REJECTED
        review.save()

        response = self.client.get(reverse("review-list-public"))
        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []