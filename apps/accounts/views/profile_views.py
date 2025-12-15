from django.shortcuts import get_object_or_404, redirect, render
from ..models.profile import UserProfile
from ..models.nickname import NicknameHistory
from django.http import Http404


def profile_by_public_id(request, public_id):
    profile = get_object_or_404(UserProfile, public_id=public_id)
    return render(
        request,
        "accounts/profile_detail.html",
        {"profile": profile},
    )


def profile_by_nickname(request, nickname):
    # 1. Current nickname → 302 on public_id
    try:
        profile = UserProfile.objects.get(nickname__iexact=nickname)
        return redirect(
            "profile_by_public_id",
            public_id=profile.public_id,
            permanent=False,  # 302
        )
    except UserProfile.DoesNotExist:
        pass

    # 2. Old nickname → 301 to the current nickname
    history = (
        NicknameHistory.objects
        .select_related("profile")
        .filter(nickname__iexact=nickname)
        .order_by("-used_at")
        .first()
    )

    if history:
        return redirect(
            "profile_by_nickname",
            nickname=history.profile.nickname,
            permanent=True,  # 301
        )

    # 3. Nickname not found
    raise Http404