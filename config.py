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
