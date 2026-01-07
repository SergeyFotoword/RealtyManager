from django.urls import path

from apps.reviews.views.review_audit import ReviewAuditView
from apps.reviews.views.review_create import ReviewCreateView
from apps.reviews.views.review_edit import ReviewEditView
from apps.reviews.views.review_delete import ReviewDeleteView
from apps.reviews.views.review_moderation import ReviewModerationView
from apps.reviews.views.review_list import (
    ReviewPublicListView,
    ReviewPrivateListView,
)

urlpatterns = [
    # CREATE
    path("", ReviewCreateView.as_view(), name="review-create"),

    # LISTS
    path("my/", ReviewPrivateListView.as_view(), name="review-list-private"),
    path("public/", ReviewPublicListView.as_view(), name="review-list-public"),

    # REVIEW ACTIONS
    path("<int:pk>/edit/", ReviewEditView.as_view(), name="review-edit"),
    path("<int:pk>/delete/", ReviewDeleteView.as_view(), name="review-delete"),
    path("<int:pk>/moderate/", ReviewModerationView.as_view(), name="review-moderate"),
    path("<int:pk>/audit/", ReviewAuditView.as_view(), name="review-audit"),
]