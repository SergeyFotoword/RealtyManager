from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.reviews.tests.base import BaseReviewTest


class ReviewAPITest(BaseReviewTest, APITestCase):
    def test_create_review_api(self):
        self.complete_stay()
        self.client.force_authenticate(user=self.tenant)

        url = reverse("review-create")
        payload = {
            "booking_id": self.booking.id,
            "rating": 5,
            "comment": "Nice stay",
        }

        response = self.client.post(url, payload, format="json")

        print("STATUS:", response.status_code)
        print("DATA:", getattr(response, "data", None))
        print("CONTENT:", response.content.decode("utf-8", errors="ignore"))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["rating"] == 5
        assert response.data["comment"] == "Nice stay"