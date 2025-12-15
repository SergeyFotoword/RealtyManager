from django.db import models
from django.conf import settings
from .role import Role


class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_reviews",
        verbose_name="Кто оставил отзыв",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_reviews",
        verbose_name="Who is the review intended for?",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="The role in which the user is assessed",
    )

    score = models.PositiveSmallIntegerField(
        verbose_name="Grade",
        help_text="An integer from 1 to 5",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Comment",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score__gte=1) & models.Q(score__lte=5),
                name="review_score_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"Review {self.reviewer} → {self.target} ({self.role.name}): {self.score}"