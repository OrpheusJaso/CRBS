from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, current_user_id,
)
from models import User

userProfileBp = Blueprint("userProfile", __name__, url_prefix="/api/profile")


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
        user.name = data["name"]
    if data.get("email"):
        user.email = data["email"]
    if data.get("password"):
        user.set_password(data["password"])
    db.session.commit()
    return jsonify(user=user.to_dict())
