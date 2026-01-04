from django.core.exceptions import ValidationError as DjangoValidationError

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.accounts.permissions import IsLandlord
from apps.bookings.models.booking import Booking
from apps.bookings.services.checkin import confirm_checkin, confirm_checkout


def _raise_drf_error(err: DjangoValidationError):
    if hasattr(err, "messages"):
        raise DRFValidationError({"detail": err.messages[0]})
    raise DRFValidationError({"detail": str(err)})


class BookingCheckinView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    @extend_schema(summary="Confirm check-in")
    def post(self, request, booking_id: int):
        booking = Booking.objects.filter(
            id=booking_id,
            landlord=request.user,
        ).first()

        if not booking:
            return Response({"detail": "Booking not found."}, status=404)

        try:
            confirm_checkin(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            _raise_drf_error(e)

        booking.refresh_from_db()
        return Response({"status": booking.status})


class BookingCheckoutView(APIView):
    permission_classes = [IsAuthenticated, IsLandlord]

    @extend_schema(summary="Confirm checkout")
    def post(self, request, booking_id: int):
        booking = Booking.objects.filter(
            id=booking_id,
            landlord=request.user,
        ).first()

        if not booking:
            return Response({"detail": "Booking not found."}, status=404)

        try:
            confirm_checkout(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            _raise_drf_error(e)

        booking.refresh_from_db()
        return Response({"status": booking.status})