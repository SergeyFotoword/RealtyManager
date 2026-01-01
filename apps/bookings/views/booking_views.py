from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.bookings.models import Booking
from apps.bookings.serializers.booking_serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
)
from apps.bookings.services.booking import (
    create_booking,
    confirm_booking,
    cancel_booking,
)


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create booking",
        request=BookingCreateSerializer,
        responses={
            201: BookingListSerializer,
            400: OpenApiResponse(description="Validation or business rule error"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Listing not found"),
        },
    )
    @transaction.atomic
    def post(self, request):
        serializer = BookingCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            booking = create_booking(
                user=request.user,
                **serializer.validated_data,
            )
        except DjangoValidationError as e:
            return Response(
                {"errors": e.messages},
                status=400,
            )

        return Response(
            BookingListSerializer(booking).data,
            status=201,
        )


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List my bookings",
        responses=BookingListSerializer(many=True),
    )
    def get(self, request):
        qs = (
            Booking.objects
            .filter(user=request.user)
            .select_related("listing")
            .order_by("-created_at")
        )

        return Response(
            BookingListSerializer(qs, many=True).data,
            status=200,
        )


class BookingConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Confirm booking (landlord)",
        responses={
            204: OpenApiResponse(description="Booking confirmed"),
            400: OpenApiResponse(description="Business rule violation"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Booking not found"),
        },
    )
    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_booking(
                booking=booking,
                user=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cancel booking",
        responses={
            204: OpenApiResponse(description="Booking cancelled"),
            400: OpenApiResponse(description="Business rule violation"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Booking not found"),
        },
    )
    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            cancel_booking(
                booking=booking,
                user=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)