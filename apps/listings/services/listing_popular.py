from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from apps.listings.models.search_query import SearchQuery


def get_popular_listings(qs, *, mode: str = "popular"):

    if mode == "popular":
        return qs.annotate(popularity=Count("views")).order_by("-popularity", "-created_at")

    if mode == "popular_uniq":
        return qs.annotate(
            popularity=Count("views__user", distinct=True)
        ).order_by("-popularity", "-created_at")

    if mode == "popular_7d":
        since = timezone.now() - timedelta(days=7)
        return qs.annotate(
            popularity=Count("views", filter=Q(views__created_at__gte=since))
        ).order_by("-popularity", "-created_at")

    return qs


def get_popular_search_queries(*, limit: int = 10):
    return (
        SearchQuery.objects
        .values("query")
        .annotate(count=Count("id"))
        .order_by("-count")
        [:limit]
    )