from django.urls import path

from apps.listings.views.listing_create import ListingCreateView
from apps.listings.views.listing_detail import ListingPublicDetailView
from apps.listings.views.listing_list_create import ListingPublicListCreateView
from apps.listings.views.listing_update import ListingUpdateView
from apps.listings.views.listing_delete import ListingDeleteView
from apps.listings.views.search_popular import PopularSearchQueryView
from apps.listings.views.search_suggestions import SearchSuggestionView


urlpatterns = [
    # PUBLIC LIST / SEARCH
    path("", ListingPublicListCreateView.as_view(), name="listing-list"),

    # CREATE
    path("create/", ListingCreateView.as_view(), name="listing-create"),

    # DETAIL
    path("<int:pk>/", ListingPublicDetailView.as_view(), name="listing-public-detail"),

    # UPDATE
    path("<int:pk>/update/", ListingUpdateView.as_view(), name="listing-update"),

    # DELETE
    path("<int:pk>/delete/", ListingDeleteView.as_view(), name="listing-delete"),

    # SEARCH ANALYTICS
    path("search/popular/", PopularSearchQueryView.as_view(), name="popular-search-queries"),
    path("search/suggestions/", SearchSuggestionView.as_view(), name="search-suggestions"),
]