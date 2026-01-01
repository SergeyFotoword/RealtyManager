from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.bookings.models import Booking
from apps.bookings.services.checkin import (
    confirm_checkin,
    confirm_checkout,
)

class BookingCheckinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Check-in booking",
        responses={
            204: OpenApiResponse(description="Checked in"),
            400: OpenApiResponse(description="Business rule violation"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Booking not found"),
        },
    )
    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_checkin(
                booking=booking,
                user=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)


class BookingCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Check-out booking",
        responses={
            204: OpenApiResponse(description="Checked out"),
            400: OpenApiResponse(description="Business rule violation"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Booking not found"),
        },
    )
    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_checkout(
                booking=booking,
                user=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)