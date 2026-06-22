from extensions import (
    Blueprint, request, jsonify, abort, db, login_required,
    role_required, current_user_id,
)
from models import Booking, Resource
from datetime import datetime
from .services import (
    notify, parse_dt, has_conflict, within_lock_window, recurrence_dates,
)

bookingBp = Blueprint("booking", __name__, url_prefix="/api/booking")

# Booking + check-in are for the people who make bookings.
BOOKERS = ("student", "staff")


@bookingBp.get("")
@login_required
def list_bookings():
    """Return the signed-in user's bookings (the Manage Bookings table)."""
    rows = (
        Booking.query.filter_by(userId=current_user_id())
        .order_by(Booking.startTime.desc())
        .all()
    )
    return jsonify(bookings=[b.to_dict() for b in rows])


@bookingBp.post("")
@role_required(*BOOKERS)
def create_booking():
    """Create a single booking (Book modal -> Confirm Booking)."""
    data = request.get_json(silent=True) or {}
    resource = Resource.query.get(data.get("resourceId"))
    if not resource:
        abort(404, description="Resource not found.")
    if resource.status != "available":
        abort(409, description=f"Resource is currently {resource.status}.")

    try:
        start = parse_dt(data.get("startTime"))
        end = parse_dt(data.get("endTime"))
    except ValueError as e:
        abort(400, description=str(e))
    if end <= start:
        abort(400, description="End time must be after start time.")

    if data.get("capacity") and int(data["capacity"]) > resource.capacity:
        abort(409, description="Requested capacity exceeds resource capacity.")
    if has_conflict(resource.resourceId, start, end):
        abort(409, description="That time slot is already booked for this resource.")

    # Specialised resources need approval; everything else is auto-confirmed.
    status = "pending" if resource.isSpecialised else "confirmed"
    booking = Booking(
        resourceId=resource.resourceId,
        userId=current_user_id(),
        purpose=data.get("purpose"),
        startTime=start,
        endTime=end,
        status=status,
    )
    db.session.add(booking)
    db.session.flush()  # assign bookingId before notifying

    if status == "pending":
        notify(current_user_id(), "Approval requested",
               f"{resource.name} requires manager approval before confirmation.",
               type="approval")
    else:
        notify(current_user_id(), "Booking confirmed",
               f"{resource.name} reserved for "
               f"{start.strftime('%d %b %Y %H:%M')}.", type="info")
    db.session.commit()
    return jsonify(booking=booking.to_dict()), 201


@bookingBp.post("/recurring")
@role_required(*BOOKERS)
def create_recurring():
    """Create a recurring series (Recurring modal). Conflicts abort the whole series."""
    data = request.get_json(silent=True) or {}
    resource = Resource.query.get(data.get("resourceId"))
    if not resource:
        abort(404, description="Resource not found.")

    pattern = data.get("recurrence", "weekly")
    if pattern not in ("weekly", "monthly"):
        abort(400, description="Recurrence must be 'weekly' or 'monthly'.")
    try:
        start = parse_dt(data.get("startTime"))
        end = parse_dt(data.get("endTime"))
        until = parse_dt(data.get("until"))
    except ValueError as e:
        abort(400, description=str(e))

    slots = list(recurrence_dates(start, end, pattern, until))
    # Check every generated date before creating anything.
    for s, e in slots:
        if has_conflict(resource.resourceId, s, e):
            abort(409, description=f"Conflict on {s.strftime('%d %b %Y %H:%M')}.")

    created = []
    for s, e in slots:
        b = Booking(resourceId=resource.resourceId, userId=current_user_id(),
                    purpose=data.get("purpose"), startTime=s, endTime=e,
                    status="confirmed", isRecurring=True, recurrence=pattern)
        db.session.add(b)
        created.append(b)
    notify(current_user_id(), "Recurring booking created",
           f"{len(created)} {pattern} sessions booked for {resource.name}.")
    db.session.commit()
    return jsonify(count=len(created),
                   bookings=[b.to_dict() for b in created]), 201


@bookingBp.put("/<int:booking_id>")
@role_required(*BOOKERS)
def modify_booking(booking_id):
    """Modify times (Modify modal). Blocked inside the 24-hour window."""
    booking = _own_booking_or_404(booking_id)
    if within_lock_window(booking.startTime):
        abort(403, description="Bookings cannot be modified within 24 hours of start.")

    data = request.get_json(silent=True) or {}
    try:
        start = parse_dt(data["startTime"]) if data.get("startTime") else booking.startTime
        end = parse_dt(data["endTime"]) if data.get("endTime") else booking.endTime
    except ValueError as e:
        abort(400, description=str(e))
    if end <= start:
        abort(400, description="End time must be after start time.")
    if has_conflict(booking.resourceId, start, end, exclude_booking_id=booking.bookingId):
        abort(409, description="That new time slot conflicts with another booking.")

    booking.startTime, booking.endTime = start, end
    if data.get("purpose") is not None:
        booking.purpose = data["purpose"]
    notify(booking.userId, "Booking modified",
           "Your updated booking details were saved.")
    db.session.commit()
    return jsonify(booking=booking.to_dict())


@bookingBp.delete("/<int:booking_id>")
@role_required(*BOOKERS)
def cancel_booking(booking_id):
    """Cancel a booking (Cancel modal). Blocked inside the 24-hour window."""
    booking = _own_booking_or_404(booking_id)
    if within_lock_window(booking.startTime):
        abort(403, description="Bookings cannot be cancelled within 24 hours of start.")
    booking.status = "cancelled"
    notify(booking.userId, "Booking cancelled",
           "The resource has been released for other users.")
    db.session.commit()
    return jsonify(booking=booking.to_dict())


@bookingBp.post("/<int:booking_id>/checkin")
@role_required(*BOOKERS)
def check_in(booking_id):
    """Confirm attendance (Check In button) to avoid no-show auto-cancel."""
    booking = _own_booking_or_404(booking_id)
    if booking.status == "cancelled":
        abort(409, description="A cancelled booking cannot be checked in.")
    booking.status = "checked_in"
    booking.checkedInAt = datetime.utcnow()
    notify(booking.userId, "Attendance confirmed",
           "Your booking will not be auto-cancelled as a no-show.", type="checkin")
    db.session.commit()
    return jsonify(booking=booking.to_dict())


def _own_booking_or_404(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking or booking.userId != current_user_id():
        abort(404, description="Booking not found.")
    return booking
