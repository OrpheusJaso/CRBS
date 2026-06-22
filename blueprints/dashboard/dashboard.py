from extensions import (
    Blueprint, jsonify, login_required, current_user_id, current_role, db,
)
from models import Booking, Resource, EquipmentRequest
from datetime import datetime, timedelta

dashboardBp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

# A booking "needs check-in" when it is confirmed and starts within this window.
CHECKIN_WINDOW_HOURS = 12


@dashboardBp.get("")
@login_required
def dashboard():
    """Role-aware dashboard metrics computed from live data.

    Returns metric cards matching the UI per role, plus the user's upcoming
    bookings so the calendar/side panels can render real data.
    """
    role = current_role()
    uid = current_user_id()
    now = datetime.utcnow()

    if role in ("student", "staff"):
        metrics, upcoming = _booker_metrics(uid, now, role)
    else:  # manager / admin -> operational view
        metrics, upcoming = _operations_metrics(now)

    return jsonify(role=role, metrics=metrics, upcoming=upcoming)


def _booker_metrics(uid, now, role):
    mine = Booking.query.filter_by(userId=uid)

    upcoming_rows = (
        mine.filter(
            Booking.startTime >= now,
            Booking.status.in_(("confirmed", "pending", "checked_in")),
        )
        .order_by(Booking.startTime.asc())
        .all()
    )

    checkin_required = mine.filter(
        Booking.status == "confirmed",
        Booking.startTime >= now,
        Booking.startTime <= now + timedelta(hours=CHECKIN_WINDOW_HOURS),
    ).count()

    if role == "student":
        third = ["Cancelled bookings",
                 mine.filter(Booking.status == "cancelled").count()]
        upcoming_label = "My upcoming bookings"
    else:  # staff
        third = ["Approval pending",
                 mine.filter(Booking.status == "pending").count()]
        upcoming_label = "Upcoming bookings"

    metrics = [
        {"label": upcoming_label, "value": len(upcoming_rows)},
        {"label": "Check-in required", "value": checkin_required},
        {"label": third[0], "value": third[1]},
    ]
    return metrics, [b.to_dict() for b in upcoming_rows]


def _operations_metrics(now):
    pending_bookings = Booking.query.filter_by(status="pending").count()
    pending_equipment = EquipmentRequest.query.filter_by(status="pending").count()
    unavailable = Resource.query.filter(Resource.status != "available").count()

    metrics = [
        {"label": "Pending approvals", "value": pending_bookings + pending_equipment},
        {"label": "Resources unavailable", "value": unavailable},
        {"label": "Active resources",
         "value": Resource.query.filter_by(status="available").count()},
    ]

    upcoming_rows = (
        Booking.query.filter(
            Booking.startTime >= now,
            Booking.status.in_(("confirmed", "pending", "checked_in")),
        )
        .order_by(Booking.startTime.asc())
        .limit(10)
        .all()
    )
    return metrics, [b.to_dict() for b in upcoming_rows]
