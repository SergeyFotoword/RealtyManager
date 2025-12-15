from django.db import models
from django.conf import settings
from .role import Role


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="User",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name="Role",
    )

    value = models.FloatField(default=0, verbose_name="Rating")
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Number of reviews")

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} [{self.role.name}]: {self.value:.2f} ({self.reviews_count})"