from apps.notifications.enums import NotificationEventType
from apps.notifications.services.base import NotificationService


class RatingNotificationService:
    @staticmethod
    def rating_updated(user, rating):
        NotificationService.send_email(
            to_user=user,
            subject="Your rating was updated",
            template="ratings/rating_updated",
            context={"rating": rating},
            event_type=NotificationEventType.RATING,
        )