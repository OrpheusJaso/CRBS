from datetime import datetime, timedelta
from extensions import db
from models import Resource, Notification, Maintenance, User

# The Controller stuff for Maintenance

VALID_RESOURCE_STATUS = ("available", "maintenance", "faulty")

def notify_all(title, message, type="info"):
    """Create a notification row (used by the bell + booking events) towards all users."""
    users = User.query.all()
    for u in users:
        db.session.add(Notification(userId=u.userId, title=title, message=message, type=type))


def parse_dt(value):
    """Parse an ISO / 'YYYY-MM-DDTHH:MM' datetime string; raise ValueError if bad."""
    if not value:
        raise ValueError("A date/time value is required.")
    return datetime.fromisoformat(value)


def has_conflict(resource_id, start, end, exclude_maintenance_id=None):
    """True if an active booking overlaps [start, end) for this resource."""
    q = Maintenance.query.filter(
        Maintenance.resourceId == resource_id,
        Maintenance.status == "scheduled",
        Maintenance.scheduledDate < end,
        db.or_(Maintenance.completedDate.is_(None), Maintenance.completedDate > start),
    )
    if exclude_maintenance_id is not None:
        q = q.filter(Maintenance.maintenanceId != exclude_maintenance_id)
    return db.session.query(q.exists()).scalar()

def edit_resource_status(resource_id, status):
    r = Resource.query.filter_by(resourceId=resource_id).first()
    if not r:
        return None
    if status not in VALID_RESOURCE_STATUS:
        return None
    r.status = status
    db.session.commit()
    return r