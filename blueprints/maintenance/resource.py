from extensions import *
from models import User

userBp = Blueprint("user", __name__, url_prefix="/api/user")

@userBp.post("/register")
def register():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}

@userBp.post("/login")
def login():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}