from extensions import *
from models import User

maintenanceBp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")

class Maintenance(db.Model):
    maintenanceId = db.Column("maintenanceId", db.Integer(11), primary_key = True, nullable = False)
    resourceId = db.Column("resourceId", db.Integer(11), foreign_key = True, nullable = False)
    scheduleDate = db.Column("scheduledDate", db.DateTime, nullable = False)
    completedDate = db.Column("completedDate", db.DateTime, nullable = False)
    status = db.Column("status", db.String(50), nullable = True)
    description = db.Column("description", db.String(255), nullable = True)
    duration = db.Column("duration", db.Integer(11), nullable = False)
    
    def __init__(self, maintenanceId, scheduledDate, completedDate, status, description, duration):
        self.__maintenanceId = maintenanceId
        self.__scheduledDate = scheduledDate
        self.__completedDate = completedDate
        self.__status = status
        self.__description = description
        self.__duration = duration
        
# Getters
    def getMaintenanceId(self):
        return self.__maintenanceId
    
    def getMaintenanceScheduledDate(self):
        return self.__scheduledDate
    
    def getMaintenanceCompletedDate(self):
        return self.__completedDate
    
    def getMaintenanceStatus(self):
        return self.__status
    
    def getMaintenanceDescription(self):
        return self.__description
    
    def getMaintenanceDuration(self):
        return self.__duration

# Setters        
    def setMaintenanceId(self, maintenanceId):
        self.__maintenanceId = maintenanceId
    
    def setMaintenanceScheduledDate(self, scheduledDate):
        self.__scheduledDate = scheduledDate
    
    def setMaintenanceCompletedDate(self, completedDate):
        self.__completedDate = completedDate
    
    def setMaintenanceStatus(self, status):
        self.__status = status
    
    def setMaintenanceDescription(self, description):
        self.__description = description
    
    def setMaintenanceDuration(self, duration):
        self.__duration = duration

@maintenanceBp.post("/create")
def create():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}

@maintenanceBp.post("/complete")
def complete():
    
    # placeholder implementation (simple JSON-compatible return)
    return {"model": "User"}