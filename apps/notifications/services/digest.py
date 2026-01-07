from __future__ import annotations

from datetime import timedelta
from django.utils import timezone

from apps.notifications.models import DigestLog, NotificationLog, NotificationPreference
from apps.notifications.services.base import NotificationService


class DigestService:
    @staticmethod
    def send_daily_digest(user) -> int:
        prefs = getattr(user, "notification_preferences", None)
        if not prefs or not prefs.daily_digest:
            return 0

        since = timezone.now() - timedelta(hours=24)

        if prefs.last_digest_sent_at and prefs.last_digest_sent_at >= since:
            return 0

        logs = NotificationLog.objects.filter(
            recipient=user,
            success=True,
            sent_at__gte=since,
        ).order_by("sent_at")

        if not logs.exists():
            return 0

        NotificationService.send_email(
            to_user=user,
            subject="Your daily notifications summary",
            template="digest/daily",
            context={
                "notifications": list(logs),
                "count": logs.count(),
                "date": timezone.localdate(),
            },
            event_type="digest",
        )

        DigestLog.objects.create(
            user=user,
            notifications_count=logs.count(),
        )

        prefs.last_digest_sent_at = timezone.now()
        prefs.save(update_fields=["last_digest_sent_at"])

        return 1