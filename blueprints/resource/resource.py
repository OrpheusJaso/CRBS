from extensions import *
from models import User

resourceBp = Blueprint("resource", __name__, url_prefix="/api/resource")

class Resource(db.Model):
    resourceId = db.Column("resourceId", db.Integer(11), primary_key = True, nullable = False)
    name = db.Column("name", db.String(100), nullable = False)
    type = db.Column("type", db.String(50), nullable = False)
    capacity = db.Column("capacity", db.Integer(11), nullable = False)
    location = db.Column("location", db.String(255), nullable = False)
    status = db.Column("status", db.String(100), nullable = False)
    description = db.Column("description", db.String(255), nullable = True)
    isSpecialised = db.Column("isSpecialised", db.Boolean, nullable = False)
    
    def __init__(self, resourceId, name, type, capacity, location, status, description, isSpecialised):
        self.__resourceId = resourceId
        self.__name = name
        self.__type = type
        self.__capacity = capacity
        self.__location = location
        self.__status = status
        self.__description = description
        self.__isSpecialised = isSpecialised
        
# Getters
    def getResourceId(self):
        return self.__resourceId
    
    def getResourceName(self):
        return self.__name
    
    def getResourceType(self):
        return self.__type
    
    def getResourceCapacity(self):
        return self.__capacity
    
    def getResourceLocation(self):
        return self.__location
    
    def getResourceStatus(self):
        return self.__status
    
    def getResourceDescription(self):
        return self.__description
    
    def getResourceIsSpecialised(self):
        return self.__isSpecialised

# Setters        
    def setResourceId(self, resourceId):
        self.__resourceId = resourceId
    
    def setResourceName(self, name):
        self.__name = name
    
    def setResourceType(self, type):
        self.__type = type
    
    def setResourceCapacity(self, capacity):
        self.__capacity = capacity
    
    def setResourceLocation(self, location):
        self.__location = location
    
    def setResourceStatus(self, status):
        self.__status = status
    
    def setResourceDescription(self, description):
        self.__description = description
    
    def setResourceIsSpecialised(self, isSpecialised):
        self.__isSpecialised = isSpecialised

@resourceBp.post("/register")
def register():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}

@resourceBp.post("/edit")
def login():
    
    # placeholder implementation (simple JSON-compatible return)x
    return {"model": "User"}

@resourceBp.post("/delete")
def delete():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}