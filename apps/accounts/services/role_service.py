"""
DEPRECATED.
Use apps.accounts.services.role instead.
"""

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from apps.accounts.models.role import Role

User = get_user_model()


def add_role_to_user(*, user: User, role_name: str) -> None:
    """
    Adds role to user if not exists.
    Idempotent operation.
    """
    role_name = role_name.lower().strip()

    role, _ = Role.objects.get_or_create(name=role_name)

    if user.roles.filter(id=role.id).exists():
        return  # already has role

    user.roles.add(role)


def remove_role_from_user(*, user: User, role_name: str) -> None:
    """
    Removes role from user.
    Guards against removing the last role.
    """
    role_name = role_name.lower().strip()

    try:
        role = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        raise ValidationError({"role": "Role does not exist."})

    if not user.roles.filter(id=role.id).exists():
        return

    if user.roles.count() <= 1:
        raise ValidationError(
            {"role": "User must have at least one role."}
        )

    user.roles.remove(role)