from django.db import models
from apps.properties.models import Property
from .rating_base import RatingAggregateMixin


class PropertyRating(RatingAggregateMixin):
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name="rating",
    )

    def __str__(self):
        return f"Rating for property {self.property_id}"