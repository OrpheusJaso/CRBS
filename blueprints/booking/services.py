"""Booking business rules: conflict checks, the 24-hour policy, recurrence."""
from datetime import datetime, timedelta
from extensions import db
from models import Booking, Resource, Notification, User
from email_service import send_email

# Booking cannot be modified/cancelled within this window of its start time.
MODIFY_LOCK_HOURS = 24

# How long before startTime a check-in is permitted (US05 E2 grace window).
CHECKIN_EARLY_MINUTES = 15

# Statuses that occupy a resource time slot.
ACTIVE_STATUSES = ("confirmed", "pending", "checked_in")


def notify(user_id, title, message, type="info"):
    """Create a notification row and best-effort email it (US06).

    The in-app Notification row is the durable primary channel; the email is a
    secondary channel that falls back silently to the row if delivery fails.
    """
    db.session.add(Notification(userId=user_id, title=title, message=message, type=type))
    # US06 normal-flow step 2: also dispatch to the student's email (best effort).
    user = User.query.get(user_id)
    if user and user.email:
        send_email(user.email, title, message)


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
    """True if `start` is less than MODIFY_LOCK_HOURS away (policy lock).

    Compares against local wall-clock time (datetime.now()) because booking
    start/end times are stored as the naive local times submitted from the
    browser. Using datetime.utcnow() here offsets the check by the server's UTC
    offset and lets bookings be cancelled/modified inside the 24-hour window.
    """
    return start - datetime.now() < timedelta(hours=MODIFY_LOCK_HOURS)


def recurrence_dates(start, end, pattern, until):
    """Yield (start, end) pairs for a weekly/monthly series up to `until`."""
    step = timedelta(weeks=1) if pattern == "weekly" else timedelta(days=30)
    cur_start, cur_end = start, end
    while cur_start <= until:
        yield cur_start, cur_end
        cur_start += step
        cur_end += step


def sweep_no_shows():
    """US05 E3: auto-cancel confirmed bookings whose window passed un-checked-in.

    A lightweight, on-demand replacement for a background scheduler — runs each
    time bookings are listed. Only `confirmed` rows are affected; `checked_in`,
    `pending`, `cancelled` and already-`no_show` rows are left alone. Returns the
    number of bookings flipped so callers can react if needed.
    """
    now = datetime.now()  # booking times are stored as local wall-clock
    stale = Booking.query.filter(
        Booking.status == "confirmed",
        Booking.endTime < now,
    ).all()
    for b in stale:
        b.status = "no_show"
        name = b.resource.name if b.resource else "your booking"
        notify(b.userId, "Booking auto-cancelled",
               f"No check-in was made for {name} during its time slot, "
               f"so it was marked as a no-show.", type="checkin")
    if stale:
        db.session.commit()
    return len(stale)
