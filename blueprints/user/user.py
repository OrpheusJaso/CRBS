from extensions import (
    Blueprint, request, jsonify, abort, db, session, login_required,
    current_user_id, current_role, ALL_ROLES,
)
from models import User
import uuid

userBp = Blueprint("user", __name__, url_prefix="/api/user")


@userBp.post("/login")
def login():
    """Authenticate and start a session (Sign in form)."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter(db.func.lower(User.email) == email).first()
    if not user or not user.check_password(password):
        abort(401, description="Invalid email or password.")

    session.permanent = True
    session["userId"] = user.userId
    session["role"] = user.role
    return jsonify(user=user.to_dict())


@userBp.post("/register")
def register():
    """Create a new account and start a session (used by the signup page)."""
    data = request.get_json(silent=True) or {}
    for field in ("name", "email", "password"):
        if not data.get(field):
            abort(400, description=f"'{field}' is required.")

    role = data.get("role", "student")
    if role not in ALL_ROLES:
        abort(400, description="Invalid role.")

    # userId is optional from the client; generate one if absent.
    user_id = data.get("userId") or f"u-{uuid.uuid4().hex[:10]}"
    if User.query.get(user_id):
        abort(409, description="User ID already exists.")
    if User.query.filter(db.func.lower(User.email) == data["email"].strip().lower()).first():
        abort(409, description="An account with that email already exists.")

    user = User(userId=user_id, name=data["name"],
                email=data["email"].strip(), role=role)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    # Log the new user straight in so they land in the app.
    session.permanent = True
    session["userId"] = user.userId
    session["role"] = user.role
    return jsonify(user=user.to_dict()), 201


@userBp.post("/logout")
def logout():
    """Clear the session."""
    session.clear()
    return jsonify(status="ok")


@userBp.get("/me")
@login_required
def me():
    """Return the signed-in user (header context / role)."""
    user = User.query.get(current_user_id())
    if not user:
        session.clear()
        abort(401)
    return jsonify(user=user.to_dict())
