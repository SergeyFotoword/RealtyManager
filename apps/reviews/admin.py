from django.contrib import admin

from apps.reviews.models.review import Review
from apps.reviews.models.review_audit import ReviewAudit
from apps.reviews.models.user_rating import UserRating
from apps.reviews.models.property_rating import PropertyRating


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking_id",
        "direction",
        "rating",
        "moderation_status",
        "is_hidden",
        "reviewer_id",
        "target_id",
        "created_at",
    )
    list_filter = ("direction", "moderation_status", "is_hidden", "created_at")
    search_fields = ("id", "booking__id", "reviewer__username", "target__username")
    ordering = ("-created_at",)
    raw_id_fields = ("booking", "reviewer", "target", "role", "property_rating")


@admin.register(ReviewAudit)
class ReviewAuditAdmin(admin.ModelAdmin):
    list_display = ("id", "review_id", "action", "actor_id", "from_status", "to_status", "created_at")
    list_filter = ("action", "from_status", "to_status", "created_at")
    search_fields = ("id", "review__id", "actor__username")
    ordering = ("-created_at",)
    raw_id_fields = ("review", "actor")


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "reviews_count", "total_score", "average", "updated_at")
    search_fields = ("user__username", "user__id")
    ordering = ("-updated_at",)
    raw_id_fields = ("user",)


@admin.register(PropertyRating)
class PropertyRatingAdmin(admin.ModelAdmin):
    list_display = ("id", "property_id", "reviews_count", "total_score", "average", "updated_at")
    search_fields = ("property__id",)
    ordering = ("-updated_at",)
    raw_id_fields = ("property",)
