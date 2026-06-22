from flask import (
    Blueprint, jsonify, request, Flask, session, abort, render_template,
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, date
from functools import wraps
import re

db = SQLAlchemy()
migrate = Migrate()

# Roles available in the system (mirrors the UI prototype's data-roles).
ALL_ROLES = ("student", "staff", "manager", "admin")


def current_user_id():
    """Return the userId stored in the session, or None if not signed in."""
    return session.get("userId")


def current_role():
    """Return the role of the signed-in user, or None."""
    return session.get("role")


def login_required(view):
    """Reject the request with 401 if there is no active session."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user_id():
            abort(401)
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    """Allow only the given roles; 401 if anonymous, 403 if wrong role."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user_id():
                abort(401)
            if current_role() not in roles:
                abort(403, description="Your role cannot access this action.")
            return view(*args, **kwargs)
        return wrapped
    return decorator
