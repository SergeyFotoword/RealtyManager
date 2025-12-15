from django.apps import apps


def is_nickname_available(nickname: str) -> bool:
    UserProfile = apps.get_model("accounts", "UserProfile")
    NicknameHistory = apps.get_model("accounts", "NicknameHistory")

    nickname = nickname.strip()

    if UserProfile.objects.filter(nickname__iexact=nickname).exists():
        return False

    if NicknameHistory.objects.filter(nickname__iexact=nickname).exists():
        return False

    return True