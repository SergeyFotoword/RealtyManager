from django.db import models


class RatingAggregateMixin(models.Model):
    reviews_count = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    average = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def recalculate(self, *, new_score: int):
        self.reviews_count += 1
        self.total_score += int(new_score)
        self.average = self.total_score / self.reviews_count
        self.save(update_fields=["reviews_count", "total_score", "average", "updated_at"])