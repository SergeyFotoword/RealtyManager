from rest_framework import serializers

from apps.reviews.models.review_audit import ReviewAudit


class ReviewAuditSerializer(serializers.ModelSerializer):
    actor_id = serializers.IntegerField(source="actor.id", read_only=True)

    class Meta:
        model = ReviewAudit
        fields = [
            "id",
            "action",
            "actor_id",
            "from_status",
            "to_status",
            "reason",
            "created_at",
        ]
        read_only_fields = fields