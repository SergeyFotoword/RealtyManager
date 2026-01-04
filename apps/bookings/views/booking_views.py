import datetime

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsTenant, IsLandlord
from apps.bookings.models.booking import Booking
from apps.bookings.services.booking import (
    create_booking,
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


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTenant]

    @extend_schema(
        summary="Create booking",
        description=(
            "Create booking request for a listing.\n\n"
            "- Only TENANT\n"
            "- Booking created with PENDING status\n"
            "- landlord is resolved from listing.owner\n"
        ),
        examples=[
            OpenApiExample(
                "Create booking",
                value={
                    "listing_id": 10,
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-10",
                },
            )
        ],
        responses={201: dict, 400: dict},
    )
    def post(self, request):
        data = request.data

        try:
            listing = Listing.objects.select_related("owner").get(
                id=data.get("listing_id")
            )
        except Listing.DoesNotExist:
            raise DRFValidationError({"listing_id": "Listing not found."})

        try:
            start_date = datetime.date.fromisoformat(data.get("start_date"))
            end_date = datetime.date.fromisoformat(data.get("end_date"))
        except Exception:
            raise DRFValidationError("Invalid date format. Use YYYY-MM-DD.")

        try:
            booking = create_booking(
                listing=listing,
                tenant=request.user,
                landlord=listing.owner,
                start_date=start_date,
                end_date=end_date,
            )
        except DjangoValidationError as e:
            _raise_drf_error(e)

        return Response(
            _booking_to_dict(booking),
            status=status.HTTP_201_CREATED,
        )


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
    permission_classes = [IsAuthenticated, IsLandlord]

    @extend_schema(
        summary="Confirm booking",
        description="Only listing owner can confirm booking.",
        responses={200: dict},
    )
    def post(self, request, booking_id: int):
        booking = Booking.objects.filter(
            id=booking_id,
            landlord=request.user,
        ).first()

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
    permission_classes = [IsAuthenticated, IsLandlord]

    @extend_schema(
        summary="Reject booking",
        responses={200: dict},
    )
    def post(self, request, booking_id: int):
        booking = Booking.objects.filter(
            id=booking_id,
            landlord=request.user,
        ).first()

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
        booking = Booking.objects.filter(
            id=booking_id,
            tenant=request.user,
        ).first()

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