from django.db import models


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


class Property(models.Model):
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
        help_text="Этаж квартиры"
    )

    total_floors = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Этажность здания"
    )

    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="properties",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_property_type_display()} · {self.rooms} rooms"