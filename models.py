"""Database models for the Campus Resource Booking System.

All models live here so they share one SQLAlchemy metadata and `create_all`
can build the whole schema. No database connection is opened at import time.
"""
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class TimestampMixin:
    """Adds created_at / updated_at columns to any model."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(db.Model):
    __tablename__ = "user"

    userId = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # student | staff | manager | admin  -> drives role-based access
    role = db.Column(db.String(20), nullable=False, default="student")

    bookings = db.relationship("Booking", backref="user", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    def to_dict(self):
        return {
            "userId": self.userId,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


class Resource(db.Model):
    __tablename__ = "resource"

    resourceId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)       # meeting room / lab / projector ...
    capacity = db.Column(db.Integer, nullable=False, default=0)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="available")  # available/maintenance/faulty
    description = db.Column(db.String(255), nullable=True)
    isSpecialised = db.Column(db.Boolean, nullable=False, default=False)     # requires approval

    bookings = db.relationship("Booking", backref="resource", lazy=True)

    def to_dict(self):
        return {
            "resourceId": self.resourceId,
            "name": self.name,
            "type": self.type,
            "capacity": self.capacity,
            "location": self.location,
            "status": self.status,
            "description": self.description,
            "isSpecialised": self.isSpecialised,
        }


class Booking(TimestampMixin, db.Model):
    __tablename__ = "booking"

    bookingId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resourceId = db.Column(db.Integer, db.ForeignKey("resource.resourceId"), nullable=False)
    userId = db.Column(db.String(50), db.ForeignKey("user.userId"), nullable=False)
    purpose = db.Column(db.String(255), nullable=True)
    startTime = db.Column(db.DateTime, nullable=False)
    endTime = db.Column(db.DateTime, nullable=False)
    # confirmed | pending | cancelled | checked_in | no_show
    status = db.Column(db.String(30), nullable=False, default="confirmed")
    isRecurring = db.Column(db.Boolean, nullable=False, default=False)
    recurrence = db.Column(db.String(20), nullable=True)   # weekly / monthly
    checkedInAt = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "bookingId": self.bookingId,
            "resourceId": self.resourceId,
            "resourceName": self.resource.name if self.resource else None,
            "userId": self.userId,
            "purpose": self.purpose,
            "startTime": self.startTime.isoformat() if self.startTime else None,
            "endTime": self.endTime.isoformat() if self.endTime else None,
            "status": self.status,
            "isRecurring": self.isRecurring,
            "recurrence": self.recurrence,
            "checkedInAt": self.checkedInAt.isoformat() if self.checkedInAt else None,
        }


class Notification(db.Model):
    __tablename__ = "notification"

    notificationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.String(50), db.ForeignKey("user.userId"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(30), nullable=False, default="info")  # info/maintenance/checkin/approval
    isRead = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "notificationId": self.notificationId,
            "userId": self.userId,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "isRead": self.isRead,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Maintenance(db.Model):
    __tablename__ = "maintenance"

    maintenanceId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resourceId = db.Column(db.Integer, db.ForeignKey("resource.resourceId"), nullable=False)
    scheduledDate = db.Column(db.DateTime, nullable=False)
    completedDate = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=True, default="scheduled")
    description = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "maintenanceId": self.maintenanceId,
            "resourceId": self.resourceId,
            "scheduledDate": self.scheduledDate.isoformat() if self.scheduledDate else None,
            "completedDate": self.completedDate.isoformat() if self.completedDate else None,
            "status": self.status,
            "description": self.description,
            "duration": self.duration,
        }


class Equipment(db.Model):
    __tablename__ = "equipment"

    equipmentId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resourceId = db.Column(db.Integer, db.ForeignKey("resource.resourceId"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    isSpecialised = db.Column(db.Boolean, nullable=False, default=False)
    # good | degraded | faulty | broken
    condition = db.Column(db.String(50), nullable=False, default="good")

    def to_dict(self):
        return {
            "equipmentId": self.equipmentId,
            "resourceId": self.resourceId,
            "name": self.name,
            "type": self.type,
            "quantity": self.quantity,
            "isSpecialised": self.isSpecialised,
            "condition": self.condition,
        }


class EquipmentRequest(db.Model):
    """A staff request to use specialised equipment (Equipment Request form)."""
    __tablename__ = "equipment_request"

    requestId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.String(50), db.ForeignKey("user.userId"), nullable=False)
    equipmentName = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(500), nullable=True)
    requestedDate = db.Column(db.DateTime, nullable=True)
    attendees = db.Column(db.Integer, nullable=True)
    # pending | approved | rejected
    status = db.Column(db.String(20), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref="equipment_requests", lazy=True)

    def to_dict(self):
        return {
            "requestId": self.requestId,
            "userId": self.userId,
            "requesterName": self.user.name if self.user else None,
            "equipmentName": self.equipmentName,
            "purpose": self.purpose,
            "requestedDate": self.requestedDate.isoformat() if self.requestedDate else None,
            "attendees": self.attendees,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
