from django.contrib import admin
from django.db.models import Count, Q

from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "property",
        "price_eur",
        "status",
        "active_bookings_count",
        "created_at",
    )

    list_select_related = ("owner", "property")
    list_filter = ("status",)
    search_fields = (
        "title",
        "owner__username",
        "owner__email",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "owner",
                "property",
            )
        }),
        ("Pricing & status", {
            "fields": (
                "price_eur",
                "status",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            active_bookings=Count(
                "bookings",
                filter=Q(bookings__status__in=["pending", "confirmed"]),
            )
        )

    def active_bookings_count(self, obj):
        return obj.active_bookings

    active_bookings_count.short_description = "Active bookings"