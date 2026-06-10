from extensions import *
from models import User

resourceBp = Blueprint("user", __name__, url_prefix="/api/user")

@resourceBp.post("/resource")
def resource():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}

@resourceBp.post("/login")
def login():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}