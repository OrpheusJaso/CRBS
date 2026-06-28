from extensions import (
    Blueprint, request, jsonify, abort, db, login_required,
    role_required, current_user_id,
)
from models import Booking, Resource
from datetime import datetime, timedelta
from storage import save_upload, DOC_EXTS
from .services import (
    notify, parse_dt, has_conflict, within_lock_window, recurrence_dates,
    sweep_no_shows, CHECKIN_EARLY_MINUTES,
)

bookingBp = Blueprint("booking", __name__, url_prefix="/api/booking")

# Booking + check-in are for the people who make bookings.
BOOKERS = ("student", "staff")


def _payload():
    """Return (data, files) so a route works for both JSON and multipart posts.

    Specialised/recurring bookings carry a supporting document, so the Search
    page submits multipart form-data; plain bookings still send JSON.
    """
    if request.files or request.form:
        return request.form, request.files
    return (request.get_json(silent=True) or {}), {}


@bookingBp.get("")
@login_required
def list_bookings():
    """Return the signed-in user's bookings (the Manage Bookings table)."""
    sweep_no_shows()  # US05 E3: lazily auto-cancel missed check-ins on view.
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
    data, files = _payload()
    resource = _lookup_resource(data.get("resourceId"))
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

    # US04 A1/E1: specialised resources require a supporting document + approval.
    document = None
    if resource.isSpecialised:
        upload = files.get("document") if files else None
        if not upload or not upload.filename:
            abort(400, description="A supporting document is required for this resource.")
        document = save_upload(upload, DOC_EXTS)

    status = "pending" if resource.isSpecialised else "confirmed"
    booking = Booking(
        resourceId=resource.resourceId,
        userId=current_user_id(),
        purpose=data.get("purpose"),
        startTime=start,
        endTime=end,
        status=status,
        documentPath=document,
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
    data, files = _payload()
    resource = _lookup_resource(data.get("resourceId"))

    pattern = data.get("recurrence", "weekly")
    if pattern not in ("weekly", "monthly"):
        abort(400, description="Recurrence must be 'weekly' or 'monthly'.")
    try:
        start = parse_dt(data.get("startTime"))
        end = parse_dt(data.get("endTime"))
        until = parse_dt(data.get("until"))
    except ValueError as e:
        abort(400, description=str(e))
    if end <= start:
        abort(400, description="End time must be after start time.")

    # US04 A1/E1: recurring bookings always require a supporting document.
    upload = files.get("document") if files else None
    if not upload or not upload.filename:
        abort(400, description="A supporting document is required for recurring bookings.")
    document = save_upload(upload, DOC_EXTS)

    slots = list(recurrence_dates(start, end, pattern, until))
    # Check every generated date before creating anything.
    for s, e in slots:
        if has_conflict(resource.resourceId, s, e):
            abort(409, description=f"Conflict on {s.strftime('%d %b %Y %H:%M')}.")

    created = []
    for s, e in slots:
        b = Booking(resourceId=resource.resourceId, userId=current_user_id(),
                    purpose=data.get("purpose"), startTime=s, endTime=e,
                    status="pending", isRecurring=True, recurrence=pattern,
                    documentPath=document)
        db.session.add(b)
        created.append(b)
    notify(current_user_id(), "Approval requested",
           f"{len(created)} {pattern} sessions for {resource.name} await "
           f"manager approval.", type="approval")
    db.session.commit()
    return jsonify(count=len(created),
                   bookings=[b.to_dict() for b in created]), 201


def _lookup_resource(resource_id):
    """Resolve a resourceId from JSON (int) or form (str); 404 if missing."""
    try:
        resource = Resource.query.get(int(resource_id)) if resource_id else None
    except (TypeError, ValueError):
        resource = None
    if not resource:
        abort(404, description="Resource not found.")
    return resource


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
    """Confirm attendance (Check In button), enforcing the valid time window.

    US05 E2: too early -> rejected. US05 E3: window already passed -> the
    booking is marked no-show rather than checked in.
    """
    booking = _own_booking_or_404(booking_id)
    if booking.status in ("cancelled", "no_show"):
        abort(409, description="This booking can no longer be checked in.")
    if booking.status == "pending":
        abort(409, description="This booking is awaiting approval and cannot be checked in yet.")
    if booking.status == "checked_in":
        abort(409, description="You have already checked in for this booking.")

    now = datetime.utcnow()
    if now < booking.startTime - timedelta(minutes=CHECKIN_EARLY_MINUTES):
        abort(403, description="Please wait until the check-in time.")
    if now > booking.endTime:
        # Missed the whole window — auto-cancel as a no-show (US05 E3).
        booking.status = "no_show"
        notify(booking.userId, "Booking auto-cancelled",
               "The check-in window has passed, so the booking was marked as a no-show.",
               type="checkin")
        db.session.commit()
        abort(409, description="The check-in window has passed; the booking was marked as a no-show.")

    booking.status = "checked_in"
    booking.checkedInAt = now
    notify(booking.userId, "Attendance confirmed",
           "Your booking will not be auto-cancelled as a no-show.", type="checkin")
    db.session.commit()
    return jsonify(booking=booking.to_dict())


def _own_booking_or_404(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking or booking.userId != current_user_id():
        abort(404, description="Booking not found.")
    return booking
