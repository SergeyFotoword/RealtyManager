from apps.reviews.services.review import create_review
from apps.reviews.tests.base import BaseReviewTest
from apps.reviews.models.property_rating import PropertyRating


class PropertyRatingPolicyTest(BaseReviewTest):
    def test_tenant_review_affects_property_rating(self):
        self.complete_stay()

        create_review(
            booking=self.booking,
            reviewer=self.tenant,
            rating=5,
            role=self.role_landlord,
        )

        property_rating = self.property.rating
        property_rating.refresh_from_db()

        assert property_rating.reviews_count == 1
        assert property_rating.average == 5

    def test_landlord_review_does_not_affect_property_rating(self):
        self.complete_stay()

        create_review(
            booking=self.booking,
            reviewer=self.landlord,
            rating=4,
            role=self.role_tenant,
        )

        assert not PropertyRating.objects.filter(property=self.property).exists()