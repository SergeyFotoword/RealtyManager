from datetime import timedelta
from django.utils import timezone

from apps.listings.models.search_query import SearchQuery

DEDUP_WINDOW_MINUTES = 5

def save_search_query(*, query: str, user=None):

    if not query:
        return

    query = query.strip()
    if len(query) < 2:
        return

    user_obj = user if user and user.is_authenticated else None
    since = timezone.now() - timedelta(minutes=DEDUP_WINDOW_MINUTES)

    exists = SearchQuery.objects.filter(
        query=query,
        user=user_obj,
        created_at__gte=since,
    ).exists()

    if exists:
        return

    SearchQuery.objects.create(
        query=query,
        user=user_obj,
    )