from django.urls import path
from apps.listings.views.listing_list import ListingPublicListView, ListingMyListView
from apps.listings.views.search_popular import PopularSearchQueryView
from apps.listings.views.search_suggestions import SearchSuggestionView
from apps.listings.views.listing_detail import ListingPublicDetailView

urlpatterns = [
    path("listings/public/", ListingPublicListView.as_view(), name="listing-public-list"),
    path(
        "listings/public/<int:pk>/",
        ListingPublicDetailView.as_view(),
        name="listing-public-detail",
    ),
    path("listings/my/", ListingMyListView.as_view(), name="listing-my-list"),
    path("search/popular/", PopularSearchQueryView.as_view(), name="popular-search-queries"),
    path("search/suggestions/", SearchSuggestionView.as_view(), name="search-suggestions"),
]