from datetime import timedelta
from django.utils import timezone
from django.db.models import Count

from apps.listings.models.search_query import SearchQuery


def get_popular_search_queries(*, days: int | None = None, limit: int = 10):
    qs = SearchQuery.objects.all()

    if days is not None:
        since = timezone.now() - timedelta(days=days)
        qs = qs.filter(created_at__gte=since)

    return (
        qs.values("query")
        .annotate(count=Count("id"))
        .order_by("-count")
        [:limit]
    )