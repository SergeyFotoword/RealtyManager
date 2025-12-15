from django.db import models

class NicknameHistory(models.Model):
    profile = models.ForeignKey(
        "UserProfile",
        on_delete=models.CASCADE,
        related_name="nickname_history",
    )
    nickname = models.CharField(max_length=32)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_at"]
        indexes = [
            models.Index(fields=["nickname"]),
        ]

    def __str__(self):
        return f"{self.nickname} → {self.profile_id}"