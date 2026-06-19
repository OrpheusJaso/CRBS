from extensions import *
import models

load_dotenv('.venv')
app = Flask(__name__, template_folder='templates')
app.permanent_session_lifetime = timedelta(days=30)
csrf = CSRFProtect(app) 

def _init_extensions(app: Flask) -> None:
    """Bind SQLAlchemy and Flask-Migrate to the app instance."""
    db.init_app(app)
    migrate.init_app(app, db)
    
def _register_blueprints(app: Flask) -> None:
    """Register all blueprints. Imported here to avoid circular imports."""
    from blueprints import register_blueprints
    register_blueprints(app)

def _register_error_handlers(app: Flask) -> None:
    """Centralised JSON error responses for common HTTP errors."""
 
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e.description)), 400
 
    @app.errorhandler(401)
    def unauthorised(e):
        return jsonify(error="Unauthorised."), 401
 
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error="Forbidden."), 403
 
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error=str(e.description)), 404
 
    @app.errorhandler(409)
    def conflict(e):
        return jsonify(error=str(e.description)), 409
 
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="An unexpected error occurred."), 500

@app.route('/')
def hello_world():
    return render_template('index.html')
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port = 5555, debug=True)
    