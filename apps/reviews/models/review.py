from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.bookings.models.booking import Booking
from apps.accounts.models.role import Role


class ReviewDirection(models.TextChoices):
    TENANT_TO_LANDLORD = "tenant_to_landlord", "Tenant → Landlord"
    LANDLORD_TO_TENANT = "landlord_to_tenant", "Landlord → Tenant"


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
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    comment = models.TextField(
        blank=True,
        help_text="Optional text review",
    )

    language = models.CharField(
        max_length=8,
        blank=True,
        help_text="ISO language code, e.g. en, de, ru",
    )

    # moderation / future
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden by moderation",
    )

    moderation_status = models.CharField(
        max_length=16,
        choices=[
            ("approved", "Approved"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
        ],
        default="approved",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            #  You can't leave a review for yourself
            models.CheckConstraint(
                condition=~models.Q(reviewer=models.F("target")),
                name="reviewer_is_not_target",
            ),

            # one review per destination per booking
            models.UniqueConstraint(
                fields=["booking", "direction"],
                name="unique_review_per_booking_direction",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Review #{self.pk} "
            f"{self.direction} "
            f"({self.rating}/5)"
        )