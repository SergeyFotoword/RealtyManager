from django.utils import timezone
from datetime import date, timedelta
from .base import BaseReviewTest
from apps.reviews.services.review import create_review
from ...bookings.models.booking import Booking


class RatingCreationTest(BaseReviewTest):

    def test_rating_created_on_first_review(self):
        self.booking.checkin_at = timezone.now()
        self.booking.checkout_at = timezone.now()
        self.booking.save()

        create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_tenant,
        )

        rating = self.landlord.rating
        assert rating.reviews_count == 1
        assert rating.average == 5


class RatingUpdateTest(BaseReviewTest):
    def test_rating_accumulates_reviews(self):
        # первая бронь
        self.booking.checkin_at = timezone.now()
        self.booking.checkout_at = timezone.now()
        self.booking.save()

        create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_tenant,
        )

        booking2 = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            landlord=self.landlord,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
        )

        booking2.checkin_at = timezone.now()
        booking2.checkout_at = timezone.now()
        booking2.save()

        create_review(
            booking=booking2,
            reviewer=self.tenant,
            rating=3,
            role=self.role_tenant,
        )

        self.landlord.refresh_from_db()

        rating = self.landlord.rating
        assert rating.reviews_count == 2
        assert rating.average == 4