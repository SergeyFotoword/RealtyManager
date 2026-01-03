from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.accounts.services.nickname import is_nickname_available
from apps.accounts.models.profile import UserProfile


NICKNAME_CHANGE_COOLDOWN = timedelta(days=30)

def change_nickname(profile, new_nickname: str)  -> UserProfile:
    """
    Domain service.
    Raises django.core.exceptions.ValidationError.
    Must be converted to DRF ValidationError at API boundary.
    """

    new_nickname = new_nickname.strip()

    if profile.nickname == new_nickname:
        return profile

    # Rate-limit
    if profile.nickname_updated_at:
        if timezone.now() - profile.nickname_updated_at < NICKNAME_CHANGE_COOLDOWN:
            remaining = NICKNAME_CHANGE_COOLDOWN - (timezone.now() - profile.nickname_updated_at)
            raise ValidationError(
                {
                    "nickname": (
                        f"You can change your nickname again in "
                        f"{remaining.days} days."
                    )
                }
            )

    #  Checking the availability of a nickname
    if not is_nickname_available(new_nickname):
        raise ValidationError(
            {"nickname": "This nickname has already been used in the system and is unavailable."}
        )

    profile.nickname = new_nickname
    profile.nickname_updated_at = timezone.now()
    profile.save()
    return profile