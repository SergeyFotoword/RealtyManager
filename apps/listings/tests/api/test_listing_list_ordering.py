from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.constants import ListingOrderBy
from apps.listings.models.models import ListingStatus
from apps.listings.tests.base import BaseListingTest


class ListingListOrderingAPITest(BaseListingTest, APITestCase):

    def test_unknown_order_by_is_ignored(self):
        self.create_listing(status=ListingStatus.ACTIVE)
        self.create_listing(status=ListingStatus.ACTIVE)

        url = reverse("listing-public-list")
        response = self.client.get(url, {"order_by": "abracadabra"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_options_returns_order_by_choices(self):
        url = reverse("listing-public-list")
        response = self.client.options(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_by_choices", response.data)
        self.assertEqual(
            set(response.data["order_by_choices"]),
            ListingOrderBy.ALL,
        )