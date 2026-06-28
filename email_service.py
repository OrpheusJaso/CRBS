"""Best-effort secondary email channel for notifications (US06).

The primary notification channel is in-app: every alert is written to the
Notification table (always persisted and viewable on the Notifications page).
This module adds the *secondary* email channel described in US06 normal flow
step 2, and implements the US06 A1 exception path:

    attempt send -> on failure retry -> on total failure return False so the
    caller simply relies on the in-app notification that already exists.

It never raises: a mail problem must never break a booking, cancellation or
issue report. Email is opt-in -- with no MAIL_* configuration (the default for
the prototype) sending is skipped and reported as a delivery failure, which
still exercises the A1 fallback to the web notification system.
"""
import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger("crbs.email")


def email_enabled():
    """True only when an SMTP destination has been configured and enabled."""
    cfg = current_app.config
    return bool(
        cfg.get("MAIL_ENABLED")
        and cfg.get("MAIL_SERVER")
        and cfg.get("MAIL_DEFAULT_SENDER")
    )


def send_email(to_email, subject, body):
    """Try to deliver an email; retry on failure; return True/False.

    Returns False (never raises) when email is disabled or delivery fails after
    all retries, signalling the caller to rely on the in-app notification.
    """
    if not to_email:
        return False
    if not email_enabled():
        # US06 A1: no email channel available -> fall back to in-app notification.
        log.debug("Email disabled; in-app notification retained for %s", to_email)
        return False

    cfg = current_app.config
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["MAIL_DEFAULT_SENDER"]
    msg["To"] = to_email
    msg.set_content(body)

    attempts = 1 + max(0, int(cfg.get("MAIL_MAX_RETRIES", 1)))
    for attempt in range(1, attempts + 1):
        try:
            _deliver(cfg, msg)
            log.info("Email delivered to %s on attempt %s.", to_email, attempt)
            return True
        except Exception as exc:  # best effort: must not propagate to the request
            log.warning("Email attempt %s/%s to %s failed: %s",
                        attempt, attempts, to_email, exc)
    log.error("Email to %s failed after %s attempts; in-app notification retained.",
              to_email, attempts)
    return False


def _deliver(cfg, msg):
    """Open an SMTP connection and send one message. Raises on any failure."""
    host = cfg["MAIL_SERVER"]
    port = int(cfg.get("MAIL_PORT", 587))
    timeout = int(cfg.get("MAIL_TIMEOUT", 10))
    if cfg.get("MAIL_USE_SSL"):
        server = smtplib.SMTP_SSL(host, port, timeout=timeout)
    else:
        server = smtplib.SMTP(host, port, timeout=timeout)
    try:
        if cfg.get("MAIL_USE_TLS"):
            server.starttls()
        if cfg.get("MAIL_USERNAME"):
            server.login(cfg["MAIL_USERNAME"], cfg.get("MAIL_PASSWORD", ""))
        server.send_message(msg)
    finally:
        try:
            server.quit()
        except Exception:
            pass
