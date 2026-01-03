from django.urls import path
from apps.listings.views.listing_list import ListingPublicListView, ListingMyListView
from apps.listings.views.search_popular import PopularSearchQueryView
from apps.listings.views.search_suggestions import SearchSuggestionView
from apps.listings.views.listing_detail import ListingPublicDetailView
from apps.listings.views.listing_create import ListingCreateView
from apps.listings.views.listing_update import ListingUpdateView
from apps.listings.views.listing_delete import ListingDeleteView

urlpatterns = [
    path("listings/", ListingCreateView.as_view(), name="listing-create"),
    path("listings/<int:pk>/", ListingUpdateView.as_view(), name="listing-update"),
    path("listings/<int:pk>/delete/", ListingDeleteView.as_view(), name="listing-delete"),
    
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