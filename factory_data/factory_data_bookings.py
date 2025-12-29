from __future__ import annotations

import random
from datetime import date, timedelta, datetime

import factory
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.bookings.models import Booking, BookingStatus
from apps.listings.models import Listing, ListingStatus

from ._pool import make_picker

User = get_user_model()
ROLE_TENANT = "TENANT"


# helpers

def _generate_dates(status: str) -> tuple[date, date]:
    """
    Generates a valid booking date range.
    GUARANTEE: end_date > start_date
    """
    start = date.today() - timedelta(days=random.randint(30, 180))
    duration = random.randint(2, 14)
    end = start + timedelta(days=duration)
    return start, end


def _generate_status() -> str:
    return random.choices(
        [
            BookingStatus.COMPLETED,
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
            BookingStatus.REJECTED,
        ],
        weights=[40, 30, 15, 15],
        k=1,
    )[0]


# pickers

pick_listing = make_picker(
    lambda: Listing.objects.filter(
        status=ListingStatus.ACTIVE,
        is_deleted=False,
    ),
    what="active listings",
)

pick_tenant = make_picker(
    lambda: User.objects.filter(roles__name=ROLE_TENANT),
    what="tenants",
)


# factory

class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking
        exclude = ("_dates",)

    listing = factory.LazyFunction(pick_listing)
    tenant = factory.LazyFunction(pick_tenant)

    @factory.lazy_attribute
    def landlord(self):
        return self.listing.owner

    status = factory.LazyFunction(_generate_status)

    # start_date / end_date MUST be set BEFORE INSERT
    @factory.lazy_attribute
    def _dates(self) -> tuple[date, date]:
        return _generate_dates(self.status)

    @factory.lazy_attribute
    def start_date(self) -> date:
        return self._dates[0]

    @factory.lazy_attribute
    def end_date(self) -> date:
        return self._dates[1]

    # Optional timeline fields (filled post-insert)
    checkin_at = None
    checkout_at = None
    confirmed_at = None
    cancelled_at = None

    @factory.post_generation
    def timeline(self, create, extracted, **kwargs):
        """
        Build a consistent booking timeline.
        Called AFTER INSERT — safe for nullable fields only.
        """
        if not create:
            return

        start_date = self.start_date
        end_date = self.end_date

        if self.status == BookingStatus.COMPLETED:
            checkin_at = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())
            ) + timedelta(hours=14)  # 14:00 check-in

            checkout_at = timezone.make_aware(
                datetime.combine(end_date, datetime.min.time())
            ) + timedelta(hours=11)  # 11:00 checkout

            self.checkin_at = checkin_at
            self.checkout_at = checkout_at
            self.confirmed_at = checkin_at - timedelta(days=2)

        elif self.status == BookingStatus.CONFIRMED:
            self.confirmed_at = timezone.now() - timedelta(days=2)

        elif self.status == BookingStatus.CANCELLED:
            self.cancelled_at = timezone.now() - timedelta(days=3)

        self.save(
            update_fields=[
                "checkin_at",
                "checkout_at",
                "confirmed_at",
                "cancelled_at",
            ]
        )


# runner

@transaction.atomic
def run(bookings_count: int = 140) -> None:
    print("Creating bookings…")

    if not Listing.objects.filter(
        status=ListingStatus.ACTIVE,
        is_deleted=False,
    ).exists():
        raise RuntimeError("No active listings found. Run listings seeder first.")

    if not User.objects.filter(roles__name=ROLE_TENANT).exists():
        raise RuntimeError("No tenants found. Run accounts seeder first.")

    BookingFactory.create_batch(bookings_count)

    print(f"Bookings generated: {bookings_count}")