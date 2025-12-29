from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.reviews.models.review import ReviewModerationStatus
from apps.reviews.tests.base import BaseReviewTest


class ReviewListAPITest(BaseReviewTest, APITestCase):
    def test_public_list_shows_only_visible_public(self):
        self.complete_stay()

        review = self.create_review_as_tenant()

        url = reverse("review-list-public")
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert len(resp.data["results"]) == 1
        assert resp.data["results"][0]["id"] == review.id

        # hidden => disappears from public
        review.is_hidden = True
        review.save(update_fields=["is_hidden"])

        resp = self.client.get(url, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0
        assert resp.data["results"] == []

        # approved but removed => disappears from public
        review.is_hidden = False
        review.moderation_status = ReviewModerationStatus.USER_REMOVED
        review.save(update_fields=["is_hidden", "moderation_status"])

        resp = self.client.get(url, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0
        assert resp.data["results"] == []

        # pending => disappears from public
        review.moderation_status = ReviewModerationStatus.PENDING
        review.save(update_fields=["moderation_status"])

        resp = self.client.get(url, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 0
        assert resp.data["results"] == []

    def test_private_list_includes_user_removed_and_hidden(self):
        self.complete_stay()
        self.client.force_authenticate(user=self.tenant)

        review = self.create_review_as_tenant()
        review.moderation_status = ReviewModerationStatus.USER_REMOVED
        review.is_hidden = True
        review.save(update_fields=["moderation_status", "is_hidden"])

        url = reverse("review-list-private")
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert len(resp.data["results"]) == 1

        item = resp.data["results"][0]
        assert item["id"] == review.id
        assert item["moderation_status"] == ReviewModerationStatus.USER_REMOVED
        assert item["is_hidden"] is True