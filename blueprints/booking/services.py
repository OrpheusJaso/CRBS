"""Booking business rules: conflict checks, the 24-hour policy, recurrence."""
from datetime import datetime, timedelta
from extensions import db
from models import Booking, Resource, Notification

# Booking cannot be modified/cancelled within this window of its start time.
MODIFY_LOCK_HOURS = 24

# Statuses that occupy a resource time slot.
ACTIVE_STATUSES = ("confirmed", "pending", "checked_in")


def notify(user_id, title, message, type="info"):
    """Create a notification row (used by the bell + booking events)."""
    db.session.add(Notification(userId=user_id, title=title, message=message, type=type))


def parse_dt(value):
    """Parse an ISO / 'YYYY-MM-DDTHH:MM' datetime string; raise ValueError if bad."""
    if not value:
        raise ValueError("A date/time value is required.")
    return datetime.fromisoformat(value)


def has_conflict(resource_id, start, end, exclude_booking_id=None):
    """True if an active booking overlaps [start, end) for this resource."""
    q = Booking.query.filter(
        Booking.resourceId == resource_id,
        Booking.status.in_(ACTIVE_STATUSES),
        Booking.startTime < end,
        Booking.endTime > start,
    )
    if exclude_booking_id is not None:
        q = q.filter(Booking.bookingId != exclude_booking_id)
    return db.session.query(q.exists()).scalar()


def within_lock_window(start):
    """True if `start` is less than MODIFY_LOCK_HOURS away (policy lock)."""
    return start - datetime.utcnow() < timedelta(hours=MODIFY_LOCK_HOURS)


def recurrence_dates(start, end, pattern, until):
    """Yield (start, end) pairs for a weekly/monthly series up to `until`."""
    step = timedelta(weeks=1) if pattern == "weekly" else timedelta(days=30)
    cur_start, cur_end = start, end
    while cur_start <= until:
        yield cur_start, cur_end
        cur_start += step
        cur_end += step
