from django.conf import settings
from django.db import models

from apps.reviews.models.review import Review, ReviewModerationStatus


class ReviewAuditAction(models.TextChoices):
    CREATED = "created", "Created"
    EDITED = "edited", "Edited"

    USER_REMOVED = "user_removed", "Removed by user"
    MODERATOR_REMOVED = "moderator_removed", "Removed by moderator"

    MODERATOR_RESTORED = "moderator_restored", "Moderator restored"
    MODERATOR_HIDDEN = "moderator_hidden", "Moderator hidden"
    MODERATOR_UNHIDDEN = "moderator_unhidden", "Moderator unhidden"


class ReviewAudit(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    action = models.CharField(
        max_length=32,
        choices=ReviewAuditAction.choices,
    )

    from_status = models.CharField(
        max_length=32,
        choices=ReviewModerationStatus.choices,
        null=True,
        blank=True,
    )

    to_status = models.CharField(
        max_length=32,
        choices=ReviewModerationStatus.choices,
        null=True,
        blank=True,
    )

    reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]