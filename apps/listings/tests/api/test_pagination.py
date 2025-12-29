from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.tests.base import BaseListingTest


class PaginationAPITest(BaseListingTest, APITestCase):

    def test_list_is_paginated(self):
        for _ in range(15):
            self.create_listing()

        url = reverse("listing-public-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 15)