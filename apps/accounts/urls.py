from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.review_views import ReviewViewSet
from .views.rating_views import UserRatingsView
from .views.role_views import RoleListView
from .views.user_views import UserListView
from .views.profile_views import profile_by_nickname, profile_by_public_id
from .views.me_views import MeNicknameView

router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:user_id>/ratings/", UserRatingsView.as_view(), name="user-ratings"),
    path("users/<uuid:public_id>/", profile_by_public_id, name="profile_by_public_id"),
    path("me/nickname/", MeNicknameView.as_view(), name="me-nickname"),
    path("@<str:nickname>/", profile_by_nickname, name="profile_by_nickname"),
]