from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models import ListingStatus
from apps.listings.tests.base import BaseListingTest


class ListingStatusAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.owner = self.create_user()
        self.other_user = self.create_user()

        self.listing = self.create_listing(
            owner=self.owner,
            status=ListingStatus.ACTIVE,
        )

        self.update_url = reverse(
            "listing-update",
            kwargs={"pk": self.listing.id},
        )
        self.public_list_url = reverse("listing-public-list")
        self.my_list_url = reverse("listing-my-list")

    def test_active_listing_visible_in_public_list(self):
        response = self.client.get(self.public_list_url)

        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.listing.id, ids)

    def test_inactive_listing_hidden_from_public_list(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(
            self.update_url,
            {"status": ListingStatus.INACTIVE},
        )

        response = self.client.get(self.public_list_url)
        ids = [item["id"] for item in response.data["results"]]

        self.assertNotIn(self.listing.id, ids)

    def test_owner_sees_inactive_listing_in_my_list(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(
            self.update_url,
            {"status": ListingStatus.INACTIVE},
        )

        response = self.client.get(self.my_list_url)
        ids = [item["id"] for item in response.data["results"]]

        self.assertIn(self.listing.id, ids)

    def test_only_owner_can_change_status(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.update_url,
            {"status": ListingStatus.INACTIVE},
        )

        self.assertEqual(response.status_code, 403)

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, ListingStatus.ACTIVE)

    def test_anonymous_user_cannot_change_status(self):
        response = self.client.patch(
            self.update_url,
            {"status": ListingStatus.INACTIVE},
        )

        self.assertEqual(response.status_code, 401)