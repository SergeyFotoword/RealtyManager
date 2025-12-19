from django.urls import path

from apps.reviews.views.review_audit import ReviewAuditView
from apps.reviews.views.review_create import ReviewCreateView
from apps.reviews.views.review_edit import ReviewEditView
from apps.reviews.views.review_delete import ReviewDeleteView
from apps.reviews.views.review_moderation import ReviewModerationView
from apps.reviews.views.review_list import (ReviewPublicListView, ReviewPrivateListView)

urlpatterns = [
    path("reviews/", ReviewCreateView.as_view(), name="review-create"),
    path("reviews/my/", ReviewPrivateListView.as_view(), name="review-list-private"),
    path("reviews/public/", ReviewPublicListView.as_view(), name="review-list-public"),
    path("reviews/<int:pk>/edit/", ReviewEditView.as_view(), name="review-edit"),
    path("reviews/<int:pk>/delete/", ReviewDeleteView.as_view(), name="review-delete"),
    path("reviews/<int:pk>/moderate/", ReviewModerationView.as_view(), name="review-moderate"),
    path("reviews/<int:pk>/audit/", ReviewAuditView.as_view(), name="review-audit"),

]