def normalize_city(city: str) -> str:
    """
    Normalize city name without changing case.
    - strips leading/trailing spaces
    - collapses multiple spaces into one
    """
    if not city:
        return city
    return " ".join(city.strip().split())