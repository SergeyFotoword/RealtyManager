from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsTenant, IsLandlord
from apps.bookings.models.booking import Booking
from apps.bookings.serializers.booking_serializers import BookingCreateSerializer, BookingListSerializer
from apps.bookings.services.booking import (
    # create_booking,
    confirm_booking,
    reject_booking,
    cancel_booking,
)

Listing = apps.get_model("listings", "Listing")


def _raise_drf_error(err: DjangoValidationError):
    if hasattr(err, "message_dict"):
        raise DRFValidationError(err.message_dict)
    if hasattr(err, "messages"):
        raise DRFValidationError({"detail": err.messages[0]})
    raise DRFValidationError({"detail": str(err)})


def _booking_to_dict(b: Booking) -> dict:
    return {
        "id": b.id,
        "listing_id": b.listing_id,
        "tenant_id": b.tenant_id,
        "landlord_id": b.landlord_id,
        "start_date": b.start_date,
        "end_date": b.end_date,
        "status": b.status,
        "created_at": b.created_at,
        "confirmed_at": b.confirmed_at,
        "cancelled_at": b.cancelled_at,
        "checkin_at": b.checkin_at,
        "checkout_at": b.checkout_at,
    }


class BookingCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsTenant]
    serializer_class = BookingCreateSerializer

    @extend_schema(
        summary="Create booking",
        description=(
            "Create booking request for a listing.\n\n"
            "- Only TENANT\n"
            "- Booking created with PENDING status\n"
            "- landlord is resolved from listing.owner\n"
        ),
        responses={201: BookingListSerializer, 400: dict},
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="My bookings (tenant)",
        responses={200: list},
    )
    def get(self, request):
        qs = Booking.objects.filter(tenant=request.user)
        return Response([_booking_to_dict(b) for b in qs])


class BookingConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Confirm booking",
        description="Only listing owner can confirm booking.",
        responses={200: dict},
    )
    def post(self, request, booking_id: int):
        # IMPORTANT: do NOT filter by landlord here — that causes false 404
        booking = Booking.objects.filter(id=booking_id).first()

        if not booking:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            confirm_booking(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            _raise_drf_error(e)

        booking.refresh_from_db()
        return Response(_booking_to_dict(booking))


class BookingRejectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Reject booking",
        responses={200: dict},
    )
    def post(self, request, booking_id: int):
        # IMPORTANT: do NOT filter by landlord here — that causes false 404
        booking = Booking.objects.filter(id=booking_id).first()

        if not booking:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            reject_booking(booking=booking, landlord=request.user)
        except DjangoValidationError as e:
            _raise_drf_error(e)

        booking.refresh_from_db()
        return Response(_booking_to_dict(booking))


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated, IsTenant]

    @extend_schema(
        summary="Cancel booking",
        responses={200: dict},
    )
    def post(self, request, booking_id: int):
        # IMPORTANT: do NOT filter by tenant here — service validates ownership
        booking = Booking.objects.filter(id=booking_id).first()

        if not booking:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            cancel_booking(booking=booking, user=request.user)
        except DjangoValidationError as e:
            _raise_drf_error(e)

        booking.refresh_from_db()
        return Response(_booking_to_dict(booking))
