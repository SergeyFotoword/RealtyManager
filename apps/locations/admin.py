from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "country",
        "state",
        "city",
        "postal_code",
        "street",
        "house_number",
    )

    list_filter = (
        "country",
        "state",
    )

    search_fields = (
        "city",
        "postal_code",
        "street",
    )

    ordering = ("country", "state", "city", "postal_code")