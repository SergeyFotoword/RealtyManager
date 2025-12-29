from datetime import timedelta
from django.utils import timezone

from apps.listings.models.search_query import SearchQuery

DEDUP_WINDOW_MINUTES = 5

STOP_WORDS = {
    "and", "or", "the", "a", "an", "of",
    "to", "in", "on", "for", "with",
}

def normalize_query(query: str) -> str:
    query = query.strip().lower()
    return " ".join(query.split())

def save_search_query(*, query: str, user=None):

    if not query:
        return

    query = normalize_query(query)

    if len(query) < 2:
        return

    if query in STOP_WORDS:
        return

    user_obj = user if user and user.is_authenticated else None
    since = timezone.now() - timedelta(minutes=DEDUP_WINDOW_MINUTES)

    if SearchQuery.objects.filter(
        query=query,
        user=user_obj,
        created_at__gte=since,
    ).exists():
        return

    SearchQuery.objects.create(
        query=query,
        user=user_obj,
    )