import uuid
from django.db import models
from django.conf import settings
from django.templatetags.static import static
from rest_framework.exceptions import ValidationError
from apps.accounts.services.nickname import is_nickname_available


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nickname = models.CharField(max_length=32, unique=True, null=True, blank=True)
    nickname_updated_at = models.DateTimeField(null=True, blank=True)
    avatar = models.FileField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile {self.user.username}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static("img/default_avatar.webp")

    def clean(self):
        super().clean()
