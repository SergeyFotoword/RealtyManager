import django_filters
from apps.listings.models import Listing


class ListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price_eur", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="price_eur", lookup_expr="lte"
    )

    min_rooms = django_filters.NumberFilter(
        field_name="property__rooms", lookup_expr="gte"
    )
    max_rooms = django_filters.NumberFilter(
        field_name="property__rooms", lookup_expr="lte"
    )

    property_type = django_filters.CharFilter(
        field_name="property__property_type"
    )

    city = django_filters.CharFilter(
        field_name="property__city", lookup_expr="icontains"
    )

    class Meta:
        model = Listing
        fields = []