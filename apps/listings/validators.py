from rest_framework.exceptions import ValidationError
from apps.listings.constants import ListingOrderBy


def validate_order_by(order_by: str | None):
    """
    Validate public order_by query param.
    """
    if order_by is None:
        return

    if order_by not in ListingOrderBy.ALL:
        raise ValidationError(
            {
                "order_by": (
                    f"Invalid value '{order_by}'. "
                    f"Allowed values: {', '.join(sorted(ListingOrderBy.PUBLIC))}"
                )
            }
        )