from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models.listing_view import ListingView
from apps.listings.tests.base import BaseListingTest


class ListingDetailViewTrackingAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.listing = self.create_listing()

    def test_anonymous_user_creates_listing_view(self):
        url = reverse(
            "listing-public-detail",
            kwargs={"pk": self.listing.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ListingView.objects.count(), 1)

        view = ListingView.objects.first()
        self.assertEqual(view.listing, self.listing)
        self.assertIsNone(view.user)

    def test_authenticated_user_creates_listing_view(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        url = reverse(
            "listing-public-detail",
            kwargs={"pk": self.listing.id},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ListingView.objects.count(), 1)

        view = ListingView.objects.first()
        self.assertEqual(view.listing, self.listing)
        self.assertEqual(view.user, user)

    def test_multiple_views_are_recorded(self):
        url = reverse(
            "listing-public-detail",
            kwargs={"pk": self.listing.id},
        )

        self.client.get(url)
        self.client.get(url)

        self.assertEqual(ListingView.objects.count(), 2)