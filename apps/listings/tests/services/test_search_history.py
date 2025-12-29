from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.listings.models.search_query import SearchQuery
from apps.listings.services.search_history import save_search_query
from apps.listings.tests.base import BaseListingTest


class SearchHistoryServiceTest(BaseListingTest, TestCase):

    def test_query_is_normalized_to_lowercase(self):
        user = self.create_user()

        save_search_query(query="Berlin", user=user)
        save_search_query(query="berlin", user=user)

        self.assertEqual(SearchQuery.objects.count(), 1)
        self.assertTrue(
            SearchQuery.objects.filter(query="berlin").exists()
        )

    def test_query_whitespace_is_normalized(self):
        user = self.create_user()

        save_search_query(query="  Berlin   Apartment ", user=user)

        sq = SearchQuery.objects.get()
        self.assertEqual(sq.query, "berlin apartment")

    def test_stop_word_is_not_saved(self):
        user = self.create_user()

        save_search_query(query="and", user=user)
        save_search_query(query="the", user=user)

        self.assertEqual(SearchQuery.objects.count(), 0)

    def test_same_user_same_query_is_deduplicated(self):
        user = self.create_user()

        save_search_query(query="berlin", user=user)
        save_search_query(query="berlin", user=user)

        self.assertEqual(SearchQuery.objects.count(), 1)

    def test_same_user_same_query_after_time_window_is_saved(self):
        user = self.create_user()

        save_search_query(query="berlin", user=user)

        sq = SearchQuery.objects.get()
        SearchQuery.objects.filter(id=sq.id).update(
            created_at=timezone.now() - timedelta(minutes=10)
        )

        save_search_query(query="berlin", user=user)

        self.assertEqual(SearchQuery.objects.count(), 2)

    def test_anonymous_user_is_deduplicated(self):
        save_search_query(query="berlin", user=None)
        save_search_query(query="berlin", user=None)

        self.assertEqual(SearchQuery.objects.count(), 1)

    def test_different_users_same_query_are_not_deduplicated(self):
        user1 = self.create_user()
        user2 = self.create_user()

        save_search_query(query="berlin", user=user1)
        save_search_query(query="berlin", user=user2)

        self.assertEqual(SearchQuery.objects.count(), 2)