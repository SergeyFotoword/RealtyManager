from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.services.availability import get_blocked_intervals
from apps.listings.models import Listing


class ListingAvailabilityView(APIView):
    """
    Public endpoint to retrieve blocked booking intervals for a listing.

    This endpoint is used by the frontend calendar to display
    unavailable dates based on existing bookings.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get listing availability (blocked intervals)",
        description=(
            "Returns blocked booking intervals for a listing within the given "
            "date range.\n\n"
            "Rules:\n"
            "- `start` and `end` query parameters are REQUIRED\n"
            "- Dates must be in YYYY-MM-DD format\n"
            "- `start` must be before `end`\n"
            "- Blocked intervals are calculated based on existing bookings "
            "(CONFIRMED and, depending on business rules, PENDING)\n"
        ),
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
            200: OpenApiResponse(
                description="Blocked date intervals",
            ),
            400: OpenApiResponse(
                description="Invalid or missing date parameters",
            ),
            404: OpenApiResponse(
                description="Listing not found",
            ),
        },
    )
    def get(self, request, listing_id: int):
        """
        GET /api/bookings/listings/{listing_id}/availability/?start=YYYY-MM-DD&end=YYYY-MM-DD
        """
        listing = get_object_or_404(Listing, pk=listing_id)

        start_raw = request.query_params.get("start")
        end_raw = request.query_params.get("end")

        start_date = parse_date(start_raw) if start_raw else None
        end_date = parse_date(end_raw) if end_raw else None

        if not start_date or not end_date:
            return Response(
                {
                    "detail": (
                        "Invalid or missing start/end date. "
                        "Use YYYY-MM-DD format."
                    )
                },
                status=400,
            )

        if start_date >= end_date:
            return Response(
                {"detail": "Start date must be before end date."},
                status=400,
            )

        blocked_intervals = get_blocked_intervals(
            listing=listing,
            start_date=start_date,
            end_date=end_date,
        )

        return Response(blocked_intervals, status=200)