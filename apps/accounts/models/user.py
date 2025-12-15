from django.contrib.auth.models import AbstractUser
from django.db import models
from .role import Role


class User(AbstractUser):
    roles = models.ManyToManyField(Role, related_name="users", blank=True)

    phone = models.CharField(max_length=20, blank=True)

    def has_role(self, role_name: str) -> bool:
        return self.roles.filter(name=role_name).exists()

    def __str__(self):
        return f"{self.username}"
        return f"{self.username} ({self.get_role_display()})"