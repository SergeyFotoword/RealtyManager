from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.tests.base import BaseListingTest

class ListingSearchAPITest(BaseListingTest, APITestCase):

    def test_search_by_title(self):
        self.create_listing(title="Cozy apartment Berlin")
        self.create_listing(title="House in Munich")

        url = reverse("listing-public-list")
        resp = self.client.get(url, {"search": "Berlin"})

        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert "Berlin" in resp.data[0]["title"]

    def test_filter_by_price_range(self):
        self.create_listing(price_eur=500)
        self.create_listing(price_eur=1200)

        url = reverse("listing-public-list")
        resp = self.client.get(url, {"price_min": 600, "price_max": 1300})

        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["price_eur"] == "1200.00" or resp.data[0]["price_eur"] == 1200

    def test_filter_by_rooms_min(self):
        self.create_listing(rooms=1)
        self.create_listing(rooms=3)

        url = reverse("listing-public-list")
        resp = self.client.get(url, {"rooms_min": 2})

        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["rooms"] == 3

    def test_filter_by_property_type(self):
        self.create_listing(property_type="apartment")
        self.create_listing(property_type="house")

        url = reverse("listing-public-list")
        resp = self.client.get(url, {"property_type": "house"})

        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["property_type"] == "house"

    def test_ordering_by_price_desc(self):
        self.create_listing(price_eur=500)
        self.create_listing(price_eur=1200)

        url = reverse("listing-public-list")
        resp = self.client.get(url, {"order_by": "price_desc"})

        assert resp.status_code == 200
        assert len(resp.data) == 2
        assert float(resp.data[0]["price_eur"]) >= float(resp.data[1]["price_eur"])
