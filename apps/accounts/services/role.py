from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models.role import Role

ROLE_TENANT = "TENANT"
ROLE_LANDLORD = "LANDLORD"


def _norm(role_name: str) -> str:
    # UPPERCASE (TENANT/LANDLORD).
    return (role_name or "").strip().upper()


@transaction.atomic
def add_role_to_user(*, user, role_name: str) -> None:
    """
    Idempotently adds a role to a user.
    Repeated calls will not create a duplicate (in M2M, this is a single user_id + role_id pair).
    """
    role_name = _norm(role_name)
    if not role_name:
        raise ValidationError({"role": "Role is required."})

    role, _ = Role.objects.get_or_create(name=role_name)
    user.roles.add(role)


@transaction.atomic
def remove_role_from_user(*, user, role_name: str) -> None:
    """
    Removes a role from a user, but:
    - the last role cannot be deleted
    - LANDLORD cannot be deleted if there are associated properties/listings
    """
    role_name = _norm(role_name)

    if role_name == ROLE_LANDLORD:
        if user.properties.exists() or user.listings.exists():
            raise ValidationError({
                "role": "Cannot remove LANDLORD role while user owns properties or listings."
            })

    try:
        role = Role.objects.get(name=role_name)
    except Role.DoesNotExist:
        raise ValidationError({"role": "Role does not exist."})

    if not user.roles.filter(id=role.id).exists():
        return

    if user.roles.count() <= 1:
        raise ValidationError({"role": "User must have at least one role."})

    user.roles.remove(role)