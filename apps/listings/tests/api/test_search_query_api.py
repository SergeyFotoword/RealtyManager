from django.urls import reverse
from rest_framework.test import APITestCase

from apps.listings.models.search_query import SearchQuery
from apps.listings.tests.base import BaseListingTest


class SearchQueryAPITest(BaseListingTest, APITestCase):

    def test_search_query_is_saved(self):
        self.create_listing()

        url = reverse("listing-public-list")
        response = self.client.get(url, {"search": "Berlin"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            SearchQuery.objects.filter(query="Berlin").exists()
        )