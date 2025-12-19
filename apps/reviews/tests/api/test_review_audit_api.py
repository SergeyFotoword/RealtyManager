from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.reviews.models.review_audit import ReviewAuditAction
from apps.reviews.tests.base import BaseReviewTest


class ReviewAuditAPITest(BaseReviewTest, APITestCase):
    def test_author_can_view_audit(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        self.client.force_authenticate(user=self.tenant)

        url = reverse("review-audit", args=[review.id])
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1
        assert resp.data[0]["action"] in {ReviewAuditAction.CREATED, ReviewAuditAction.EDITED}
        # created log exists somewhere; ordering is "-created_at", so created может быть не первым
        assert any(item["action"] == ReviewAuditAction.CREATED for item in resp.data)

    def test_target_can_view_audit(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        self.client.force_authenticate(user=self.landlord)

        url = reverse("review-audit", args=[review.id])
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_200_OK
        assert any(item["action"] == ReviewAuditAction.CREATED for item in resp.data)

    def test_non_participant_cannot_view_audit(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        stranger = self.create_user(username="stranger")
        self.client.force_authenticate(user=stranger)

        url = reverse("review-audit", args=[review.id])
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_moderator_can_view_audit(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        moderator = self.create_user(username="mod", is_staff=True)
        self.client.force_authenticate(user=moderator)

        url = reverse("review-audit", args=[review.id])
        resp = self.client.get(url, format="json")

        assert resp.status_code == status.HTTP_200_OK

    def test_reason_is_saved_in_audit(self):
        self.complete_stay()
        review = self.create_review_as_tenant()

        moderator = self.create_user(is_staff=True)
        self.client.force_authenticate(user=moderator)

        moderate_url = reverse("review-moderate", args=[review.id])
        reason = "Spam content"

        resp = self.client.post(
            moderate_url,
            {"action": "remove", "reason": reason},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK

        audit_url = reverse("review-audit", args=[review.id])
        resp = self.client.get(audit_url)

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["action"] == ReviewAuditAction.MODERATOR_REMOVED
        assert resp.data[0]["reason"] == reason