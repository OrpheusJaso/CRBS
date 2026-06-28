from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, current_user_id,
)
from models import User
import re

userProfileBp = Blueprint("userProfile", __name__, url_prefix="/api/profile")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@userProfileBp.get("")
@login_required
def get_profile():
    """Return the current user's profile (Profile Settings page)."""
    user = User.query.get(current_user_id())
    if not user:
        abort(404, description="User not found.")
    return jsonify(user=user.to_dict())


@userProfileBp.put("")
@login_required
def update_profile():
    """Update name/email and optionally change the password."""
    user = User.query.get(current_user_id())
    if not user:
        abort(404, description="User not found.")

    data = request.get_json(silent=True) or {}

    if data.get("name"):
        user.name = data["name"].strip()

    if data.get("email"):
        email = data["email"].strip()
        if not EMAIL_RE.match(email):
            abort(400, description="Please enter a valid email address.")
        clash = User.query.filter(
            db.func.lower(User.email) == email.lower(),
            User.userId != user.userId,
        ).first()
        if clash:
            abort(409, description="An account with that email already exists.")
        user.email = email

    # US02 A1: changing the password requires the correct current password.
    if data.get("password"):
        current = data.get("currentPassword") or ""
        if not user.check_password(current):
            abort(400, description="Current password is incorrect.")
        if len(data["password"]) < 6:
            abort(400, description="New password must be at least 6 characters.")
        user.set_password(data["password"])

    db.session.commit()
    return jsonify(user=user.to_dict())
