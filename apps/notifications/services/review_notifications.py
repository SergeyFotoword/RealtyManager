from django.contrib.auth import get_user_model
from apps.notifications.enums import NotificationEventType
from apps.notifications.services.base import NotificationService

User = get_user_model()


class ReviewNotificationService:
    @staticmethod
    def new_review_for_user(review):
        """
        Notify the target user that they received a new review.
        Review model has: reviewer (writer) and target (receiver).
        """
        NotificationService.send_email(
            to_user=review.target,
            subject="You received a new review",
            template="reviews/new_review_user",
            context={"review": review},
            event_type=NotificationEventType.REVIEW,
        )

    @staticmethod
    def new_review_for_moderators(review):
        """
        Notify all staff users (moderators) that a review is pending moderation.
        """
        moderators = User.objects.filter(is_staff=True, is_active=True)
        for moderator in moderators:
            NotificationService.send_email(
                to_user=moderator,
                subject="New review pending moderation",
                template="reviews/new_review_moderator",
                context={"review": review},
                event_type=NotificationEventType.REVIEW,
            )

    @staticmethod
    def review_removed(review):
        """
        Notify the review writer that their review was removed.
        In current Review model the writer is `review.reviewer` (NOT `author`).
        """
        NotificationService.send_email(
            to_user=review.reviewer,
            subject="Your review was removed",
            template="reviews/review_removed",
            context={"review": review},
            event_type=NotificationEventType.REVIEW,
        )