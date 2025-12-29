from django.urls import path
from apps.properties.views.amenity_list import AmenityListView

urlpatterns = [
    path("amenities/", AmenityListView.as_view(), name="amenity-list"),
]