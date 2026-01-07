from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.review_views import ReviewViewSet
from .views.rating_views import UserRatingsView
from .views.user_views import UserListView
from .views.profile_views import profile_by_public_id, profile_by_nickname
from .views.me_views import MeNicknameView, MeView, MeProfileUpdateView
from .views.role_views import (
    RoleListView,
    MeBecomeLandlordView,
    MeDropLandlordView,
)

router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),

    path("roles/", RoleListView.as_view(), name="role-list"),
    path("me/become-landlord/", MeBecomeLandlordView.as_view(), name="me-become-landlord"),
    path("me/drop-landlord/", MeDropLandlordView.as_view(), name="me-drop-landlord"),

    path("users/", UserListView.as_view(), name="user-list"),
    path(
        "users/<int:user_id>/ratings/",
        UserRatingsView.as_view(),
        name="user-ratings",
    ),

    path(
        "users/<uuid:public_id>/",
        profile_by_public_id,
        name="profile_by_public_id",
    ),
    path(
        "@<str:nickname>/",
        profile_by_nickname,
        name="profile_by_nickname",
    ),
    path("me/", MeView.as_view(), name="me"),
    path("me/profile/", MeProfileUpdateView.as_view(), name="me-profile"),
    path("me/nickname/", MeNicknameView.as_view(), name="me-nickname"),
]