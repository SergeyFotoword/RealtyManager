from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.reviews.tests.base import BaseReviewTest
from apps.reviews.services.review import create_review


class ReviewEditDeleteAPITest(BaseReviewTest, APITestCase):
    def setUp(self):
        super().setUp()
        self.complete_stay()
        self.client.force_authenticate(user=self.tenant)
        self.review = create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_landlord,
            comment="initial",
        )

    def test_edit_review(self):
        url = reverse("review-edit", args=[self.review.id])
        resp = self.client.patch(url, {"rating": 4, "comment": "updated"}, format="json")
        assert resp.status_code == status.HTTP_200_OK

    def test_delete_review(self):
        url = reverse("review-delete", args=[self.review.id])
        resp = self.client.patch(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK