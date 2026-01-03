from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models import Listing
from apps.listings.tests.base import BaseListingTest


class ListingDeleteAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.owner = self.create_user()
        self.other_user = self.create_user()

        self.listing = self.create_listing(owner=self.owner)
        self.url = reverse(
            "listing-delete",
            kwargs={"pk": self.listing.id},
        )

    def test_owner_can_soft_delete_listing(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)

        listing = Listing.objects.get(id=self.listing.id)
        self.assertTrue(listing.is_deleted)
        self.assertIsNotNone(listing.deleted_at)

    def test_deleted_listing_not_visible_in_public_list(self):
        self.client.force_authenticate(user=self.owner)
        self.client.delete(self.url)

        public_url = reverse("listing-public-list")
        response = self.client.get(public_url)

        ids = [item["id"] for item in response.data["results"]]
        self.assertNotIn(self.listing.id, ids)

    def test_non_owner_cannot_delete_listing(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 403)

        listing = Listing.objects.get(id=self.listing.id)
        self.assertFalse(listing.is_deleted)

    def test_anonymous_user_cannot_delete_listing(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_deleted_listing_cannot_be_deleted_again(self):
        self.client.force_authenticate(user=self.owner)
        self.client.delete(self.url)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)