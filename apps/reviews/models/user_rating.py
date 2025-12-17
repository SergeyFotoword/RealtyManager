from django.conf import settings
from django.db import models
from .rating_base import RatingAggregateMixin


class UserRating(RatingAggregateMixin):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating",
    )

    def __str__(self):
        return f"Rating for user {self.user_id}"