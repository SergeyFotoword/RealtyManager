from django.core.management.base import BaseCommand
from apps.bookings.services.lifecycle import complete_finished_bookings


class Command(BaseCommand):
    help = "Mark finished confirmed bookings as completed"

    def handle(self, *args, **options):
        updated = complete_finished_bookings()
        self.stdout.write(
            self.style.SUCCESS(f"Completed {updated} bookings.")
        )

# run it like this: python manage.py complete_bookings