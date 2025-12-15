from django.db.models.signals import (
    post_save,
    post_delete,
    pre_save,
)
from django.dispatch import receiver
from django.db.models import Avg, Count

from apps.accounts.models.review import Review
from apps.accounts.models.rating import Rating
from apps.accounts.models.profile import UserProfile
from apps.accounts.models.nickname import NicknameHistory


def _recalculate_rating_for(user, role):
    agg = Review.objects.filter(target=user, role=role).aggregate(
        avg=Avg("score"),
        count=Count("id"),
    )

    rating, _ = Rating.objects.get_or_create(user=user, role=role)

    if agg["count"] == 0:
        rating.value = 0
        rating.reviews_count = 0
    else:
        rating.value = float(agg["avg"] or 0)
        rating.reviews_count = agg["count"]

    rating.save()


@receiver(post_save, sender=Review)
def update_rating_on_save(sender, instance: Review, **kwargs):
    _recalculate_rating_for(instance.target, instance.role)


@receiver(post_delete, sender=Review)
def update_rating_on_delete(sender, instance: Review, **kwargs):
    _recalculate_rating_for(instance.target, instance.role)

@receiver(pre_save, sender=UserProfile)
def save_nickname_history(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = UserProfile.objects.get(pk=instance.pk)
    if old.nickname and old.nickname != instance.nickname:
        NicknameHistory.objects.create(
            profile=instance,
            nickname=old.nickname,
        )