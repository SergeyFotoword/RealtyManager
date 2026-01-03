from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.listings.models import Listing
from apps.bookings.models.booking import Booking, BookingStatus
from apps.bookings.serializers.booking_serializers import (
    BookingCreateSerializer,
    BookingListSerializer,
)
from apps.bookings.services.booking import (
    create_booking,
    confirm_booking,
    reject_booking,
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
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = get_object_or_404(Listing, pk=serializer.validated_data["listing_id"])

        try:
            booking = create_booking(
                listing=listing,
                tenant=request.user,
                start_date=serializer.validated_data["start_date"],
                end_date=serializer.validated_data["end_date"],
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(BookingListSerializer(booking).data, status=201)


class _DefaultPagination(PageNumberPagination):
    page_size_query_param = "page_size"


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List my bookings (tenant)",
        parameters=[
            OpenApiParameter(
                name="scope",
                type=str,
                required=False,
                description="active|past|all (default: active)",
            )
        ],
        responses=BookingListSerializer(many=True),
    )
    def get(self, request):
        scope = (request.query_params.get("scope") or "active").lower()

        qs = (
            Booking.objects
            .filter(tenant=request.user)
            .select_related("listing")
            .order_by("-created_at")
        )

        if scope == "active":
            qs = qs.filter(status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED])
        elif scope == "past":
            qs = qs.exclude(status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED])
        elif scope == "all":
            pass
        else:
            return Response({"detail": "Invalid scope. Use active|past|all."}, status=400)

        paginator = _DefaultPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = BookingListSerializer(page, many=True).data
        return paginator.get_paginated_response(data)


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
                landlord=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)


class BookingRejectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Reject booking (landlord)",
        responses={
            204: OpenApiResponse(description="Booking rejected"),
            400: OpenApiResponse(description="Business rule violation"),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Booking not found"),
        },
    )
    @transaction.atomic
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)

        try:
            reject_booking(
                booking=booking,
                landlord=request.user,
            )
        except DjangoValidationError as e:
            return Response({"errors": e.messages}, status=400)

        return Response(status=204)


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cancel booking (tenant)",
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