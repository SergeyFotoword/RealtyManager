from django.contrib import admin

from .models.user import User
from .models.profile import UserProfile
from .models.role import Role
from .models.review import Review
from .models.rating import Rating
from .models.nickname import NicknameHistory


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "phone", "get_roles")
    search_fields = ("username", "email")
    list_filter = ("roles",)
    inlines = [UserProfileInline]

    def get_roles(self, obj):
        return ", ".join(role.name for role in obj.roles.all())
    get_roles.short_description = "Roles"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "reviewer", "target", "role", "score", "created_at")
    search_fields = (
        "reviewer__username",
        "target__username",
        "comment",
    )
    list_filter = ("role", "score", "created_at")
    autocomplete_fields = ("reviewer", "target", "role")

    list_select_related = ("reviewer", "target", "role")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "value", "reviews_count")
    search_fields = ("user__username", "role__name")
    list_filter = ("role",)
    autocomplete_fields = ("user", "role")

    list_select_related = ("user", "role")

    def has_change_permission(self, request, obj=None):
        if request.method in ("GET", "HEAD"):
            return True
        return False


@admin.register(NicknameHistory)
class NicknameHistoryAdmin(admin.ModelAdmin):
    list_display = ("nickname", "profile", "used_at")
    list_filter = ("used_at",)
    search_fields = ("nickname", "profile__nickname")
    ordering = ("-used_at",)