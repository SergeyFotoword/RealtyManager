import random
import datetime
from django.utils import timezone

from apps.bookings.models import BookingStatus
from .booking_rules import BOOKING_RULES


def generate_status() -> str:
    r = random.random()
    cumulative = 0.0

    for status, weight in BOOKING_RULES["status_distribution"]:
        cumulative += weight
        if r <= cumulative:
            return status

    return BookingStatus.CONFIRMED


def generate_dates(status: str):
    today = timezone.localdate()
    duration = random.randint(
        BOOKING_RULES["min_days"],
        BOOKING_RULES["max_days"],
    )

    if status == BookingStatus.COMPLETED:
        end_date = today - datetime.timedelta(days=random.randint(1, 30))
        start_date = end_date - datetime.timedelta(days=duration)
        return start_date, end_date

    # все остальные — настоящее / будущее
    start_date = today + datetime.timedelta(days=random.randint(0, 30))
    end_date = start_date + datetime.timedelta(days=duration)
    return start_date, end_date