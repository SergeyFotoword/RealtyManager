from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models.booking import Booking, BookingStatus


class Command(BaseCommand):
    help = "Expire pending bookings older than TTL (hours)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ttl-hours",
            type=int,
            default=24,
            help="TTL in hours for pending bookings",
        )

    def handle(self, *args, **options):
        ttl_hours = options["ttl_hours"]
        cutoff = timezone.now() - timezone.timedelta(hours=ttl_hours)

        updated = Booking.objects.filter(
            status=BookingStatus.PENDING,
            created_at__lt=cutoff,
        ).update(status=BookingStatus.EXPIRED)

        self.stdout.write(
            self.style.SUCCESS(f"Expired {updated} bookings.")
        )