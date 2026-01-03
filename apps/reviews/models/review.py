from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.bookings.models.booking import Booking
from apps.accounts.models.role import Role


class ReviewDirection(models.TextChoices):
    TENANT_TO_LANDLORD = "tenant_to_landlord", "Tenant → Landlord"
    LANDLORD_TO_TENANT = "landlord_to_tenant", "Landlord → Tenant"


class ReviewModerationStatus(models.TextChoices):
    # moderation flow
    APPROVED = "approved", "Approved"
    PENDING = "pending", "Pending"
    REJECTED = "rejected", "Rejected"

    # soft delete / removal
    USER_REMOVED = "user_removed", "Removed by user"
    MODERATOR_REMOVED = "moderator_removed", "Removed by moderator"


class ReviewQuerySet(models.QuerySet):
    def not_removed(self):
        return self.exclude(
            moderation_status__in=[
                ReviewModerationStatus.USER_REMOVED,
                ReviewModerationStatus.MODERATOR_REMOVED,
            ]
        )

    def visible_public(self):
        """
        Visible to public pages and other users:
        - approved
        - not removed
        - not hidden
        """
        return (
            self.not_removed()
            .filter(moderation_status=ReviewModerationStatus.APPROVED, is_hidden=False)
        )

    def counts_for_rating(self):
        """
        Reviews that affect rating calculation
        """
        return self.visible_public()


class Review(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )

    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )

    direction = models.CharField(
        max_length=32,
        choices=ReviewDirection.choices,
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        help_text="Role in which the user is being reviewed",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    property_rating = models.ForeignKey(
        "reviews.PropertyRating",
        on_delete=models.SET_NULL,
        related_name="reviews",
        null=True,
        blank=True,
    )

    comment = models.TextField(
        blank=True,
        default="",
        help_text="Optional text review",
    )

    language = models.CharField(
        max_length=8,
        blank=True,
        help_text="ISO language code, e.g. en, de, ru",
    )

    # moderation / visibility
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden by moderation",
    )

    moderation_status = models.CharField(
        max_length=20,
        choices=ReviewModerationStatus.choices,
        default=ReviewModerationStatus.APPROVED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    objects = ReviewQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # You can't leave a review for yourself
            models.CheckConstraint(
                condition=~models.Q(reviewer=models.F("target")),
                name="reviewer_is_not_target",
            ),

            # one review per direction per booking
            models.UniqueConstraint(
                fields=["booking", "direction"],
                name="unique_review_per_booking_direction",
            ),

            # PropertyRating only for tenant reviews
            models.CheckConstraint(
                condition=(
                    models.Q(
                        direction=ReviewDirection.TENANT_TO_LANDLORD,
                        property_rating__isnull=False,
                    )
                    | models.Q(
                        direction=ReviewDirection.LANDLORD_TO_TENANT,
                        property_rating__isnull=True,
                    )
                ),
                name="property_rating_only_for_tenant_reviews",
            ),
        ]

    def __str__(self) -> str:
        return f"Review #{self.pk} {self.direction} ({self.rating}/5)"
