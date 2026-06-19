from extensions import *
from models import User

equipmentBp = Blueprint("equipment", __name__, url_prefix="/api/equipment")

class equipment(db.Model):
    equipmentId = db.Column("equipmentId", db.Integer(11), primary_key = True, nullable = False)
    resourceId = db.Column("resourceId", db.Integer(11), foreign_key = True, nullable = False)
    name = db.Column("name", db.String(100), nullable = False)
    type = db.Column("type", db.String(50), nullable = False)
    quantity = db.Column("quantity", db.Integer(11), nullable = False)
    isSpecialised = db.Column("isSpecialised", db.Boolean, nullable = False)
    condition = db.Column("condition", db.String(50), nullable = False)
    
    def __init__(self, equipmentId, name, type, quantity, location, condition, description, isSpecialised):
        self.__equipmentId = equipmentId
        self.__name = name
        self.__type = type
        self.__quantity = quantity
        self.__condition = condition
        self.__description = description
        self.__isSpecialised = isSpecialised
        
# Getters
    def getEquipmentId(self):
        return self.__equipmentId
    
    def getEquipmentName(self):
        return self.__name
    
    def getEquipmentType(self):
        return self.__type
    
    def getEquipmentQuantity(self):
        return self.__quantity
    
    def getEquipmentCondition(self):
        return self.__condition
    
    def getEquipmentDescription(self):
        return self.__description
    
    def getEquipmentIsSpecialised(self):
        return self.__isSpecialised

# Setters        
    def setEquipmentId(self, equipmentId):
        self.__equipmentId = equipmentId
    
    def setEquipmentName(self, name):
        self.__name = name
    
    def setEquipmentType(self, type):
        self.__type = type
    
    def setEquipmentQuantity(self, quantity):
        self.__quantity = quantity
    
    def setEquipmentCondition(self, condition):
        self.__condition = condition
    
    def setEquipmentDescription(self, description):
        self.__description = description
    
    def setEquipmentIsSpecialised(self, isSpecialised):
        self.__isSpecialised = isSpecialised


@equipmentBp.route("/register")
def Equipment():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}

@equipmentBp.route("/login")
def login():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}