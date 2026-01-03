from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models import ListingStatus
from apps.listings.tests.base import BaseListingTest


class ListingUpdateAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.owner = self.create_user()
        self.other_user = self.create_user()

        self.listing = self.create_listing(owner=self.owner)
        self.url = reverse("listing-update", kwargs={"pk": self.listing.id})

    def test_owner_can_update_listing(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {
                "title": "Updated title",
                "price_eur": 1500,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.title, "Updated title")
        self.assertEqual(self.listing.price_eur, 1500)

    def test_owner_can_change_status(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.url,
            {"status": ListingStatus.INACTIVE},
        )

        self.assertEqual(response.status_code, 200)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, ListingStatus.INACTIVE)

    def test_non_owner_cannot_update_listing(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {"title": "Hack attempt"},
        )

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_update_listing(self):
        response = self.client.patch(
            self.url,
            {"title": "Anonymous"},
        )

        self.assertEqual(response.status_code, 401)

    def test_deleted_listing_cannot_be_updated(self):
        self.client.force_authenticate(user=self.owner)

        self.listing.is_deleted = True
        self.listing.save()

        response = self.client.patch(
            self.url,
            {"title": "Should fail"},
        )

        self.assertEqual(response.status_code, 404)