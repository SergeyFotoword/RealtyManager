from django.core.management.base import BaseCommand

from apps.notifications.tasks import notify_expired_bookings, run_digests


class Command(BaseCommand):
    help = "Runs notification jobs: expired booking emails + rolling 24h digests."

    def handle(self, *args, **options):
        self.stdout.write("Running notification jobs...")

        notify_expired_bookings()
        self.stdout.write("✓ notify_expired_bookings done")

        run_digests()
        self.stdout.write("✓ run_digests done")

        self.stdout.write(self.style.SUCCESS("All notification jobs finished."))

# python manage.py run_notification_jobs
# 0 * * * * cd /app && /app/.venv/bin/python manage.py run_notification_jobs
