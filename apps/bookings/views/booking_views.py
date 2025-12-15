from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.bookings.models.booking import Booking
from apps.bookings.serializers.booking_serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
)
from apps.bookings.services.booking import (
    create_booking,
    confirm_booking,
    cancel_booking,
)
from apps.listings.models import Listing

class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = get_object_or_404(
            Listing,
            pk=serializer.validated_data["listing_id"],
        )

        try:
            booking = create_booking(
                listing=listing,
                tenant=request.user,
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
            )
        except DjangoValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            BookingListSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Booking.objects.filter(tenant=request.user)
        return Response(
            BookingListSerializer(qs, many=True).data
        )


class BookingConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            confirm_booking(
                booking=booking,
                landlord=request.user,
            )
        except DjangoValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            cancel_booking(
                booking=booking,
                user=request.user,
            )
        except DjangoValidationError as e:
            return Response(
                {"detail": e.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)