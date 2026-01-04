from django.conf import settings
from django.db import models
from django.utils.text import slugify

class PropertyType(models.TextChoices):
    APARTMENT = "apartment", "Apartment"
    HOUSE = "house", "House"
    STUDIO = "studio", "Studio"
    ROOM = "room", "Room"
    MAISONETTE = "maisonette", "Maisonette"
    PENTHOUSE = "penthouse", "Penthouse"
    OFFICE = "office", "Office"
    RETAIL = "retail", "Retail"
    WAREHOUSE = "warehouse", "Warehouse"
    PARKING = "parking", "Parking"
    LAND = "land", "Land"


class Amenity(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            i = 1
            while Amenity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Property(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties",
        null=True,
        blank=True,
    )

    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="properties",
        null=True,
        blank=True,
    )

    property_type = models.CharField(
        max_length=32,
        choices=PropertyType.choices,
    )

    rooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        help_text="Например 2.5 — типично для DE"
    )

    area_sqm = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    floor = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Apartment floor"
    )

    total_floors = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Number of floors of the building"
    )

    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="properties",
    )

    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="properties",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_property_type_display()} · {self.rooms} rooms"
