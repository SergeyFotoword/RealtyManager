from django.urls import path

from apps.properties.views.amenity_list import AmenityListView
from apps.properties.views.property_list import PropertyListCreateView
from apps.properties.views.property_detail import PropertyDetailView

urlpatterns = [
    path("amenities/", AmenityListView.as_view(), name="amenity-list"),
    # Property CRUD
    path("", PropertyListCreateView.as_view(), name="property-list-create"),
    path("<int:pk>/", PropertyDetailView.as_view(), name="property-detail"),
]