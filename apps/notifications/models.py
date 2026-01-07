from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db import models


class NotificationLog(models.Model):
    EVENT_BOOKING = "booking"
    EVENT_REVIEW = "review"
    EVENT_RATING = "rating"

    EVENT_CHOICES = [
        (EVENT_BOOKING, "Booking"),
        (EVENT_REVIEW, "Review"),
        (EVENT_RATING, "Rating"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_logs",
    )

    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    subject = models.CharField(max_length=255)

    # "booking/pending_created" etc.
    template = models.CharField(max_length=255)

    # safe audit/debug context (keep it small-ish)
    context = models.JSONField(default=dict, blank=True)

    sent_at = models.DateTimeField(auto_now_add=True)

    # delivery status
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self) -> str:
        return f"{self.event_type} → {self.recipient_id} [{self.subject}]"


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    instant_emails = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)

    last_digest_sent_at = models.DateTimeField(null=True, blank=True)

    def can_send_digest(self) -> bool:
        if not self.daily_digest:
            return False

        if not self.last_digest_sent_at:
            return True

        return timezone.now() >= self.last_digest_sent_at + timedelta(hours=24)


class DigestLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="digest_logs",
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    notifications_count = models.PositiveIntegerField()

    class Meta:
        ordering = ("-sent_at",)

    def __str__(self):
        return f"Digest to {self.user_id} ({self.notifications_count})"