"""Application configuration.

Uses PostgreSQL when DB_* environment variables are present (matching the
original setup), otherwise falls back to a local SQLite file so the project
runs out-of-the-box for the prototype with `flask run` and no extra setup.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _database_uri() -> str:
    user = os.environ.get("DB_USER")
    if user:
        # Full PostgreSQL configuration provided via .env
        password = os.environ.get("DB_PASS", "")
        host = os.environ.get("DB_HOST", "localhost")
        port = os.environ.get("DB_PORT", "5432")
        name = os.environ.get("DB_NAME", "crbs")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    # Zero-config fallback: SQLite file next to the project
    base_dir = os.path.abspath(os.path.dirname(__file__))
    return "sqlite:///" + os.path.join(base_dir, "crbs.db")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # The JSON API is session/origin protected; CSRF form tokens are not used.
    WTF_CSRF_ENABLED = False

    # Uploaded booking documents (US04) and issue images (US07) land here.
    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "uploads"
    )
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB cap per upload

    # Secondary email channel for notifications (US06). Opt-in and OFF by
    # default so the prototype runs with no SMTP setup -- notifications still
    # appear in-app. Set MAIL_ENABLED=true plus the MAIL_* vars in .env to
    # actually send (e.g. a Gmail app password or institutional SMTP relay).
    MAIL_ENABLED = os.environ.get("MAIL_ENABLED", "").lower() in ("1", "true", "yes")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", os.environ.get("MAIL_USERNAME")
    )
    MAIL_MAX_RETRIES = int(os.environ.get("MAIL_MAX_RETRIES", "1"))
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", "10"))
