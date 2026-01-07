from enum import StrEnum


class NotificationEventType(StrEnum):
    BOOKING = "booking"
    REVIEW = "review"
    RATING = "rating"