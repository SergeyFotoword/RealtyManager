from django.db import models

class GermanState(models.TextChoices):
    BW = "BW", "Baden-Württemberg"
    BY = "BY", "Bayern"
    BE = "BE", "Berlin"
    BB = "BB", "Brandenburg"
    HB = "HB", "Bremen"
    HH = "HH", "Hamburg"
    HE = "HE", "Hessen"
    MV = "MV", "Mecklenburg-Vorpommern"
    NI = "NI", "Niedersachsen"
    NW = "NW", "Nordrhein-Westfalen"
    RP = "RP", "Rheinland-Pfalz"
    SL = "SL", "Saarland"
    SN = "SN", "Sachsen"
    ST = "ST", "Sachsen-Anhalt"
    SH = "SH", "Schleswig-Holstein"
    TH = "TH", "Thüringen"

class Location(models.Model):
    country = models.CharField(max_length=2, default="DE")  # ISO-2
    state = models.CharField(max_length=2, choices=GermanState.choices)
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=12)
    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=32, blank=True)

    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["country"]),
            models.Index(fields=["state"]),
            models.Index(fields=["city"]),
            models.Index(fields=["postal_code"]),
            models.Index(fields=["state", "city"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["country", "state", "city", "postal_code"],
                name="unique_location_city_zip",
            )
        ]

    def __str__(self):
        return f"{self.postal_code} {self.city}, {self.state}"