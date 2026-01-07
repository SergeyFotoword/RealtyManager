from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models.profile import UserProfile
from apps.accounts.models.role import Role

User = get_user_model()


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    profile: UserProfile


def _split_name(name: str) -> tuple[str, str]:
    """
    Splits a full name into (first_name, last_name).
    If only one word provided -> goes to first_name.
    """
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    name: str = "",
    username: Optional[str] = None,
    default_role: str = "tenant",
) -> RegistrationResult:
    """
    Creates:
    - User (username defaults to email)
    - UserProfile (one-to-one)
    - assigns default role (creates Role row if missing)
    """

    email = (email or "").strip().lower()
    if not email:
        raise ValidationError({"email": "Email is required."})

    # IMPORTANT: User model is AbstractUser-based and DOES NOT enforce unique email in DB.
    # We'll enforce it at service level.
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "A user with this email already exists."})

    if username is None or not str(username).strip():
        username = email
    username = str(username).strip()

    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError({"username": "A user with this username already exists."})

    # Validate password via Django validators (AUTH_PASSWORD_VALIDATORS)
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise ValidationError({"password": list(e.messages)})

    first_name, last_name = _split_name(name)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    profile = UserProfile.objects.create(user=user)

    # Default role (tenant)
    role_obj, _ = Role.objects.get_or_create(name=default_role)
    user.roles.add(role_obj)

    return RegistrationResult(user=user, profile=profile)