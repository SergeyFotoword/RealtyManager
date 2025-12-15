from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ListingImage


@receiver(post_delete, sender=ListingImage)
def delete_listing_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)