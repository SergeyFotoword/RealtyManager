from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.bookings.models.booking import Booking
from apps.bookings.services.checkin import (
    confirm_checkin,
    confirm_checkout,
)

class BookingCheckinView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_checkin(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_checkout(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)