from django.conf import settings
from django.db import models


class Rating(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating",
    )

    reviews_count = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def recalculate(self, *, new_score: int):
        self.reviews_count += 1
        self.total_score += new_score
        self.average = self.total_score / self.reviews_count
        self.save(update_fields=[
            "reviews_count",
            "total_score",
            "average",
            "updated_at",
        ])

    def __str__(self):
        return f"Rating({self.user_id}): {self.average}"