from django.db.models import Count

from apps.listings.models.search_query import SearchQuery


def get_search_suggestions(*, prefix: str, limit: int = 5):
    if not prefix or len(prefix.strip()) < 2:
        return []

    prefix = prefix.strip()

    return (
        SearchQuery.objects
        .filter(query__istartswith=prefix)
        .values("query")
        .annotate(count=Count("id"))
        .order_by("-count")
        [:limit]
    )