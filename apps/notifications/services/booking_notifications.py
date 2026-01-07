from apps.notifications.enums import NotificationEventType
from apps.notifications.services.base import NotificationService


class BookingNotificationService:
    @staticmethod
    def pending_created(booking):
        """
        Notify landlord (listing owner) about new PENDING booking request.
        Booking model: tenant / landlord.
        """
        NotificationService.send_email(
            to_user=booking.landlord,
            subject="New booking request",
            template="booking/pending_created",
            context={
                "booking": booking,
                "listing": booking.listing,
                "tenant": booking.tenant,
            },
            event_type=NotificationEventType.BOOKING,
        )

    @staticmethod
    def confirmed(booking):
        """
        Notify tenant about CONFIRMED booking.
        """
        NotificationService.send_email(
            to_user=booking.tenant,
            subject="Your booking is confirmed",
            template="booking/confirmed",
            context={
                "booking": booking,
                "listing": booking.listing,
            },
            event_type=NotificationEventType.BOOKING,
        )

    @staticmethod
    def rejected(booking):
        """
        Notify tenant about REJECTED booking.
        """
        NotificationService.send_email(
            to_user=booking.tenant,
            subject="Your booking was rejected",
            template="booking/rejected",
            context={
                "booking": booking,
                "listing": booking.listing,
            },
            event_type=NotificationEventType.BOOKING,
        )

    @staticmethod
    def expired(booking):
        """
        Called from cron/job.
        Must be idempotent — dedup is done via NotificationLog(context.booking_id).
        """
        NotificationService.send_email(
            to_user=booking.tenant,
            subject="Booking request expired",
            template="booking/expired",
            context={
                "booking": booking,
                "listing": booking.listing,
                "booking_id": booking.id,  # ключ для дедупликации в tasks.py
            },
            event_type=NotificationEventType.BOOKING,
        )

    @staticmethod
    def cancelled(booking):
        """
        Notify landlord about CANCELLED booking (by tenant).
        """
        NotificationService.send_email(
            to_user=booking.landlord,
            subject="Booking was cancelled",
            template="booking/cancelled",
            context={
                "booking": booking,
                "listing": booking.listing,
                "tenant": booking.tenant,
            },
            event_type=NotificationEventType.BOOKING,
        )