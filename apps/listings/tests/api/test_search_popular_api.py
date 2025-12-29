from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.listings.models.search_query import SearchQuery
from apps.listings.tests.base import BaseListingTest


class PopularSearchQueryAPITest(BaseListingTest, APITestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("popular-search-queries")

    def test_popular_search_queries_without_period(self):
        SearchQuery.objects.create(query="berlin")
        SearchQuery.objects.create(query="berlin")
        SearchQuery.objects.create(query="munich")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        queries = [item["query"] for item in response.data]
        self.assertEqual(queries[0], "berlin")
        self.assertIn("munich", queries)

    def test_popular_search_queries_7d(self):
        SearchQuery.objects.create(query="berlin")

        old = SearchQuery.objects.create(query="munich")
        SearchQuery.objects.filter(id=old.id).update(
            created_at=timezone.now() - timedelta(days=10)
        )

        response = self.client.get(self.url, {"period": "7d"})

        self.assertEqual(response.status_code, 200)

        queries = [item["query"] for item in response.data]

        self.assertIn("berlin", queries)
        self.assertNotIn("munich", queries)

    def test_popular_search_queries_30d(self):
        SearchQuery.objects.create(query="berlin")

        old = SearchQuery.objects.create(query="hamburg")
        SearchQuery.objects.filter(id=old.id).update(
            created_at=timezone.now() - timedelta(days=40)
        )

        response = self.client.get(self.url, {"period": "30d"})

        self.assertEqual(response.status_code, 200)

        queries = [item["query"] for item in response.data]

        self.assertIn("berlin", queries)
        self.assertNotIn("hamburg", queries)

    def test_unknown_period_falls_back_to_all_time(self):
        SearchQuery.objects.create(query="berlin")
        SearchQuery.objects.create(query="munich")

        response = self.client.get(self.url, {"period": "100d"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)