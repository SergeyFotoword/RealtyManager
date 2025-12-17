from django.urls import path

from apps.reviews.views.review_create import ReviewCreateView
from apps.reviews.views.review_list import ReviewListView
from apps.reviews.views.review_edit import ReviewEditView
from apps.reviews.views.review_delete import ReviewDeleteView

urlpatterns = [
    path("reviews/", ReviewCreateView.as_view(), name="review-create"),
    path("reviews/my/", ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:pk>/edit/", ReviewEditView.as_view(), name="review-edit"),
    path("reviews/<int:pk>/delete/", ReviewDeleteView.as_view(), name="review-delete"),
]