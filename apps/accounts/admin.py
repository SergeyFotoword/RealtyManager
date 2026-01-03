from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models.user import User
from .models.profile import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    inlines = [UserProfileInline]

    list_display = ("id", "username", "email", "get_roles", "is_active")
    search_fields = ("username", "email")
    list_filter = ("roles", "is_active")

    def get_roles(self, obj):
        return ", ".join(role.name for role in obj.roles.all())
    get_roles.short_description = "Roles"

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        ("Roles", {"fields": ("roles",)}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "is_active"),
        }),
        ("Roles", {"classes": ("wide",), "fields": ("roles",)}),
    )

    filter_horizontal = ("groups", "user_permissions", "roles")