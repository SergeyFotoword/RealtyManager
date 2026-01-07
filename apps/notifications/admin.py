from django.contrib import admin
from apps.notifications.models import NotificationLog, DigestLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """
    Admin for NotificationLog.
    Matches NotificationLog model EXACTLY.
    """

    list_display = (
        "id",
        "recipient",
        "event_type",
        "subject",
        "success",
        "sent_at",
    )

    list_filter = (
        "event_type",
        "success",
    )

    search_fields = (
        "recipient__email",
        "subject",
        "template",
    )

    readonly_fields = (
        "sent_at",
    )

    ordering = ("-sent_at",)


@admin.register(DigestLog)
class DigestLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "notifications_count",
        "sent_at",
    )

    search_fields = (
        "user__email",
    )

    readonly_fields = (
        "sent_at",
    )

    ordering = ("-sent_at",)