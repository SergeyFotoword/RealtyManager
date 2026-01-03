from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.listings.models import Listing
from apps.bookings.services.availability import get_blocked_intervals


class ListingAvailabilityView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get listing availability (blocked intervals)",
        parameters=[
            OpenApiParameter(
                name="start",
                type=str,
                description="Start date (YYYY-MM-DD)",
                required=True,
            ),
            OpenApiParameter(
                name="end",
                type=str,
                description="End date (YYYY-MM-DD)",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Blocked date intervals"),
            400: OpenApiResponse(description="Invalid or missing date parameters"),
            404: OpenApiResponse(description="Listing not found"),
        },
    )
    def get(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)

        start = parse_date(request.query_params.get("start", ""))
        end = parse_date(request.query_params.get("end", ""))

        if not start or not end:
            return Response(
                {"detail": "Invalid or missing start/end date. Use YYYY-MM-DD."},
                status=400,
            )

        if start >= end:
            return Response(
                {"detail": "Start date must be before end date."},
                status=400,
            )

        blocked = get_blocked_intervals(
            listing=listing,
            start_date=start,
            end_date=end,
        )

        return Response(blocked, status=200)