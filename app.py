from extensions import *
from config import Config
import models


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.permanent_session_lifetime = timedelta(days=30)

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context(app)

    @app.route("/api")
    def api_index():
        return jsonify(
            service="Campus Resource Booking System",
            status="ok",
            endpoints=[
                "/api/user/login",
                "/api/resource",
                "/api/resource/search",
                "/api/booking",
                "/api/notification",
                "/api/dashboard",
                "/api/equipment/request",
                "/api/report/export",
            ],
        )

    # Ensure the upload directory exists for booking documents / issue images.
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Build the schema and seed demo data on first run.
    with app.app_context():
        db.create_all()
        from seed import seed_demo_data
        seed_demo_data()

    return app


def _init_extensions(app: Flask) -> None:
    """Bind SQLAlchemy and Flask-Migrate to the app instance."""
    db.init_app(app)
    migrate.init_app(app, db)


def _register_blueprints(app: Flask) -> None:
    """Register all blueprints. Imported here to avoid circular imports."""
    from blueprints import register_blueprints
    register_blueprints(app)


def _register_context(app: Flask) -> None:
    """Expose the signed-in user's role/name to every template.

    Lets base.html render the correct role server-side instead of shipping a
    hardcoded "Staff" placeholder that the JS corrects ~0.5s later (the flash).
    """

    @app.context_processor
    def inject_current_user():
        role = current_role()
        name = None
        if role:
            user = models.User.query.get(current_user_id())
            name = user.name if user else None
        return {"current_user_role": role, "current_user_name": name}


def _register_error_handlers(app: Flask) -> None:
    """Centralised JSON error responses for common HTTP errors."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e.description)), 400

    @app.errorhandler(401)
    def unauthorised(e):
        # Surface a custom abort(401, description=...) message (e.g. the login
        # route's "Invalid email or password.") while keeping a generic message
        # for bare abort(401) calls from the auth decorators.
        from werkzeug.exceptions import Unauthorized
        message = e.description if e.description != Unauthorized.description else "Unauthorised."
        return jsonify(error=message), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error=str(e.description)), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e.description)), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify(error=str(e.description)), 409

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="An unexpected error occurred."), 500


# `flask run` looks for this module-level app; `python app.py` also works.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
