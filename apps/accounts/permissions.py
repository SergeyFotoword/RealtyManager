from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsReviewerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user


class IsSelf(BasePermission):
    """
    Allows access only to its own user_id.
    """

    def has_permission(self, request, view):
        user_id = view.kwargs.get("user_id")
        return request.user.is_authenticated and request.user.id == user_id


class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.has_role("LANDLORD")
        )

class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.has_role("TENANT")
        )