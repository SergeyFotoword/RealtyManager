from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

from apps.listings.models.search_query import SearchQuery


def get_popular_search_queries(*, limit: int = 10):
    return (
        SearchQuery.objects
        .values("query")
        .annotate(count=Count("id"))
        .order_by("-count")
        [:limit]
    )


def get_popular_search_queries_7d(*, limit: int = 10):
    since = timezone.now() - timedelta(days=7)

    return (
        SearchQuery.objects
        .filter(created_at__gte=since)
        .values("query")
        .annotate(count=Count("id"))
        .order_by("-count")
        [:limit]
    )