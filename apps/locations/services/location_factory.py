from apps.locations.models import Location
from apps.locations.services.normalize import normalize_city


def get_or_create_location(
    *,
    country: str = "DE",
    state: str,
    city: str,
    postal_code: str,
    street: str | None = None,
    house_number: str | None = None,
):
    city = normalize_city(city)

    location, created = Location.objects.get_or_create(
        country=country,
        state=state,
        city=city,
        postal_code=postal_code,
        defaults={
            "street": street or "",
            "house_number": house_number or "",
        },
    )

    return location