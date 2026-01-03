from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models import Listing, ListingStatus
from apps.listings.tests.base import BaseListingTest


class ListingCreateAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("listing-create")

    def test_authenticated_user_can_create_listing(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        property_obj = self.create_property()

        payload = {
            "property_id": property_obj.id,
            "title": "New apartment in Berlin",
            "description": "Nice and cozy",
            "price_eur": 1200,
        }

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, 201)

        listing = Listing.objects.get()

        self.assertEqual(listing.owner, user)
        self.assertEqual(listing.title, payload["title"])
        self.assertEqual(listing.price_eur, payload["price_eur"])

    def test_listing_created_with_draft_status(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        property_obj = self.create_property()

        response = self.client.post(
            self.url,
            {
                "property_id": property_obj.id,
                "title": "Draft listing",
                "price_eur": 800,
            },
        )

        self.assertEqual(response.status_code, 201)

        listing = Listing.objects.get()
        self.assertEqual(listing.status, ListingStatus.DRAFT)

    def test_owner_is_set_automatically(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        property_obj = self.create_property()

        self.client.post(
            self.url,
            {
                "property_id": property_obj.id,
                "title": "Owner test",
                "price_eur": 900,
            },
        )

        listing = Listing.objects.get()
        self.assertEqual(listing.owner, user)

    def test_anonymous_user_cannot_create_listing(self):
        property_obj = self.create_property()

        response = self.client.post(
            self.url,
            {
                "property_id": property_obj.id,
                "title": "Should fail",
                "price_eur": 500,
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Listing.objects.count(), 0)