from django.test import TestCase

from apps.listings.services.listing_search import search_listings
from apps.listings.tests.base import BaseListingTest
from apps.properties.models import Amenity


class SearchListingsServiceTest(BaseListingTest, TestCase):

    def test_filter_by_amenities_slug(self):
        wifi = Amenity.objects.create(name="Wi-Fi", slug="wifi")

        listing_with_wifi = self.create_listing()
        listing_with_wifi.property.amenities.add(wifi)

        listing_without_wifi = self.create_listing()

        qs = search_listings(amenities="wifi")

        ids = list(qs.values_list("id", flat=True))

        self.assertIn(listing_with_wifi.id, ids)
        self.assertNotIn(listing_without_wifi.id, ids)