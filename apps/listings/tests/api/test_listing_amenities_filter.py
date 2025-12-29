from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.tests.base import BaseListingTest
from apps.properties.models import Amenity


class ListingAmenitiesFilterAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()

        self.amenity_wifi = Amenity.objects.create(
            name="Wi-Fi",
            slug="wifi",
        )

        self.listing_with_wifi = self.create_listing()
        self.listing_with_wifi.property.amenities.add(self.amenity_wifi)

        self.listing_without_wifi = self.create_listing()

    def test_filter_by_amenities_slug(self):
        url = reverse("listing-public-list")

        response = self.client.get(url, {"amenities": "wifi"})

        self.assertEqual(response.status_code, 200)

        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.listing_with_wifi.id, ids)
        self.assertNotIn(self.listing_without_wifi.id, ids)