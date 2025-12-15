from django.conf import settings
from django.db import models
from django.db.models import Q, F

class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


class Booking(models.Model):
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings_received",
        db_index=True,
    )

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=16,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )

    checkin_at = models.DateTimeField(null=True, blank=True)
    checkout_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cancelled_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=F("start_date")),
                name="booking_end_after_start",
            )
        ]

    @property
    def has_stayed(self) -> bool:
        """The fact of residence (at least check-in)."""
        return self.checkin_at is not None

    @property
    def can_leave_review(self) -> bool:
        """
        Review can be left only after actual stay:
        both check-in and check-out must be present.
        """
        return self.checkin_at is not None and self.checkout_at is not None

    def __str__(self):
        return f"Booking #{self.pk} ({self.start_date} → {self.end_date})"