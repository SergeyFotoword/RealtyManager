from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from apps.listings.models import Listing
from apps.bookings.services.availability import get_blocked_intervals

class ListingAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, listing_id):
        listing = get_object_or_404(Listing, pk=listing_id)

        try:
            start = request.query_params.get("start")
            end = request.query_params.get("end")
            if not start or not end:
                return Response(
                    {"detail": "start and end query params are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response(
                {"detail": "Invalid date format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        blocked = get_blocked_intervals(
            listing=listing,
            start_date=start,
            end_date=end,
        )

        return Response({
            "listing_id": listing.id,
            "start": start,
            "end": end,
            "blocked": blocked,
        })