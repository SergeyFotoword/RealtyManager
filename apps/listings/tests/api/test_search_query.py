from datetime import timezone, timedelta

from apps.listings.models import SearchQuery
from apps.listings.services.search_history import save_search_query
from apps.listings.services.search_popular import get_popular_search_queries_7d
from apps.listings.services.search_suggestions import get_search_suggestions


def test_search_query_is_deduplicated(db, user_factory):
    user = user_factory()

    save_search_query(query="berlin", user=user)
    save_search_query(query="berlin", user=user)

    assert SearchQuery.objects.count() == 1

def test_popular_search_queries_7d(db):
    SearchQuery.objects.create(query="berlin")
    SearchQuery.objects.create(
        query="munich",
        created_at=timezone.now() - timedelta(days=10),
    )

    data = get_popular_search_queries_7d()
    queries = [d["query"] for d in data]

    assert "berlin" in queries
    assert "munich" not in queries

def test_search_suggestions(db):
    SearchQuery.objects.create(query="berlin")
    SearchQuery.objects.create(query="berlin apartment")
    SearchQuery.objects.create(query="munich")

    data = get_search_suggestions(prefix="ber")

    queries = [d["query"] for d in data]
    assert "berlin" in queries
    assert "berlin apartment" in queries
    assert "munich" not in queries

