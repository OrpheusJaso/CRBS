from extensions import *
from models import User

userProfileBp = Blueprint("userProfile", __name__, url_prefix="/api/user")

@userProfileBp.post("/login")
def login():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}