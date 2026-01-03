from django.urls import path
from apps.bookings.views.booking_views import (
    BookingCreateView,
    MyBookingsView,
    BookingConfirmView,
    BookingRejectView,
    BookingCancelView,
)
from apps.bookings.views.checkin_views import (
    BookingCheckinView,
    BookingCheckoutView,
)
from apps.bookings.views.availability_views import ListingAvailabilityView


urlpatterns = [
    path("", BookingCreateView.as_view(), name="booking-create"),
    path("my/", MyBookingsView.as_view(), name="booking-my"),

    path("<int:booking_id>/confirm/", BookingConfirmView.as_view(), name="booking-confirm"),
    path("<int:booking_id>/reject/", BookingRejectView.as_view(), name="booking-reject"),
    path("<int:booking_id>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),

    path("<int:booking_id>/checkin/", BookingCheckinView.as_view(), name="booking-checkin"),
    path("<int:booking_id>/checkout/", BookingCheckoutView.as_view(), name="booking-checkout"),

    path(
        "listings/<int:listing_id>/availability/",
        ListingAvailabilityView.as_view(),
        name="listing-availability",
    ),
]