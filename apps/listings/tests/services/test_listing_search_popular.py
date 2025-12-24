from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from apps.listings.constants import ListingOrderBy
from apps.listings.models.models import ListingStatus
from apps.listings.models.listing_view import ListingView
from apps.listings.services.listing_search import search_listings
from apps.listings.tests.base import BaseListingTest


class ListingSearchPopularTest(BaseListingTest, TestCase):

    def test_popular_orders_by_total_views(self):
        l1 = self.create_listing(status=ListingStatus.ACTIVE)
        l2 = self.create_listing(status=ListingStatus.ACTIVE)

        ListingView.objects.create(listing=l1)
        ListingView.objects.create(listing=l1)
        ListingView.objects.create(listing=l2)

        qs = search_listings(order_by=ListingOrderBy.POPULAR)

        self.assertEqual(list(qs), [l1, l2])

    def test_popular_uniq_orders_by_unique_users(self):
        l1 = self.create_listing(status=ListingStatus.ACTIVE)
        l2 = self.create_listing(status=ListingStatus.ACTIVE)

        u1 = self.create_user()
        u2 = self.create_user()

        ListingView.objects.create(listing=l1, user=u1)
        ListingView.objects.create(listing=l1, user=u1)
        ListingView.objects.create(listing=l2, user=u1)
        ListingView.objects.create(listing=l2, user=u2)

        qs = search_listings(order_by=ListingOrderBy.POPULAR_UNIQ)

        self.assertEqual(list(qs), [l2, l1])

    def test_popular_7d_counts_only_recent_views(self):
        l1 = self.create_listing(status=ListingStatus.ACTIVE)
        l2 = self.create_listing(status=ListingStatus.ACTIVE)

        v1 = ListingView.objects.create(listing=l1)
        v2 = ListingView.objects.create(listing=l2)

        ListingView.objects.filter(id=v1.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        ListingView.objects.filter(id=v2.id).update(
            created_at=timezone.now() - timedelta(days=10)
        )

        qs = search_listings(order_by=ListingOrderBy.POPULAR_7D)

        self.assertEqual(list(qs), [l1, l2])