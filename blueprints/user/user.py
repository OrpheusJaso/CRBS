from extensions import (
    Blueprint, request, jsonify, abort, db, session, login_required,
    current_user_id, current_role, ALL_ROLES,
)
from models import User

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
    """Create a new account."""
    data = request.get_json(silent=True) or {}
    for field in ("userId", "name", "email", "password"):
        if not data.get(field):
            abort(400, description=f"'{field}' is required.")

    role = data.get("role", "student")
    if role not in ALL_ROLES:
        abort(400, description="Invalid role.")
    if User.query.get(data["userId"]) or User.query.filter(
        db.func.lower(User.email) == data["email"].lower()
    ).first():
        abort(409, description="User already exists.")

    user = User(userId=data["userId"], name=data["name"],
                email=data["email"], role=role)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
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
