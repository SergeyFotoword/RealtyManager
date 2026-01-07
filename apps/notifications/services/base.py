from __future__ import annotations

from typing import Any
from datetime import date, datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import get_language

from apps.notifications.enums import NotificationEventType
from apps.notifications.models import NotificationLog

try:
    from apps.notifications.models import NotificationPreference
except Exception:  # pragma: no cover
    NotificationPreference = None


def _normalize_context(value: Any) -> Any:
    """
    Make NotificationLog.context JSON-serializable.

    Supported:
    - datetime / date -> ISO string
    - Django model instance -> pk
    - dict / list / tuple -> recursive normalization
    """
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if hasattr(value, "pk"):
        return value.pk

    if isinstance(value, dict):
        return {k: _normalize_context(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_normalize_context(v) for v in value]

    return value


class NotificationService:
    @staticmethod
    def _resolve_language(user) -> str:
        lang = getattr(user, "language", None) or get_language() or "en"
        lang = str(lang).lower()
        return "de" if lang.startswith("de") else "en"

    @staticmethod
    def _instant_emails_enabled(user) -> bool:
        """
        Instant emails are enabled unless:
        - NotificationPreference exists
        - and instant_emails is explicitly False
        """
        if NotificationPreference is None:
            return True

        prefs = getattr(user, "notification_preferences", None)
        if not prefs:
            return True

        return bool(prefs.instant_emails)

    @staticmethod
    def send_email(
        *,
        to_user,
        subject: str,
        template: str,
        context: dict | None = None,
        event_type: str = NotificationEventType.BOOKING,
    ) -> None:

        if not getattr(to_user, "email", ""):
            NotificationLog.objects.create(
                recipient=to_user,
                event_type=event_type,
                subject=subject,
                template=template,
                context=_normalize_context(context or {}),
                success=False,
                error="Recipient has no email.",
            )
            return

        if not NotificationService._instant_emails_enabled(to_user):
            NotificationLog.objects.create(
                recipient=to_user,
                event_type=event_type,
                subject=subject,
                template=template,
                context=_normalize_context(context or {}),
                success=True,
                error="Instant emails disabled; waiting for digest.",
            )
            return

        context = context or {}

        render_context: dict[str, Any] = {
            **context,
            "platform_name": getattr(settings, "PLATFORM_NAME", "RealtyManager"),
            "user": to_user,
        }

        log_context = _normalize_context(render_context)

        language = NotificationService._resolve_language(to_user)

        text_body = render_to_string(
            f"email/{language}/{template}.txt",
            render_context,
        )

        html_body = None
        try:
            html_body = render_to_string(
                f"email/{language}/{template}.html",
                render_context,
            )
        except TemplateDoesNotExist:
            pass

        log = NotificationLog.objects.create(
            recipient=to_user,
            event_type=event_type,
            subject=subject,
            template=template,
            context=log_context,
            success=False,
            error="",
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_user.email],
        )
        if html_body:
            email.attach_alternative(html_body, "text/html")

        try:
            email.send()
            log.success = True
            log.save(update_fields=["success"])
        except Exception as exc:
            log.error = str(exc)
            log.save(update_fields=["error"])
            raise