from django.contrib.auth.models import AbstractUser
from django.db import models
from .role import Role


class User(AbstractUser):
    roles = models.ManyToManyField(Role, related_name="users", blank=True)

    def has_role(self, role_name: str) -> bool:
        role_name = (role_name or "").strip()
        if not role_name:
            return False
        return self.roles.filter(name__iexact=role_name).exists()

    def __str__(self):
        return self.username