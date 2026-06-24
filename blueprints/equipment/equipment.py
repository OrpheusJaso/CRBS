from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
    current_user_id,
)
from models import Equipment, EquipmentRequest
from datetime import datetime

equipmentBp = Blueprint("equipment", __name__, url_prefix="/api/equipment")

# Specialised equipment requests come from staff (and admins acting as staff).
REQUESTERS = ("staff", "admin")
MODIFIERS = ("manager",)

@equipmentBp.get("")
@login_required
def list_equipment():
    """Catalogue of equipment (drop-down options for the request form)."""
    return jsonify(equipment=[e.to_dict() for e in Equipment.query.all()])


@equipmentBp.post("/request")
@role_required(*REQUESTERS)
def submit_request():
    """Submit a specialised equipment request (Equipment Request form)."""
    data = request.get_json(silent=True) or {}
    name = (data.get("equipmentName") or "").strip()
    if not name:
        abort(400, description="'equipmentName' is required.")

    requested_date = None
    if data.get("requestedDate"):
        try:
            requested_date = datetime.fromisoformat(data["requestedDate"])
        except ValueError:
            abort(400, description="Invalid 'requestedDate'.")

    req = EquipmentRequest(
        userId=current_user_id(),
        equipmentName=name,
        purpose=data.get("purpose"),
        requestedDate=requested_date,
        attendees=data.get("attendees"),
        status="pending",
    )
    db.session.add(req)

    # Notify the requester that the approval workflow has started.
    from blueprints.booking.services import notify
    notify(current_user_id(), "Request submitted",
           f"Your request for {name} is pending manager approval.",
           type="approval")
    db.session.commit()
    return jsonify(request=req.to_dict()), 201


@equipmentBp.get("/request")
@login_required
def my_requests():
    """List the current user's equipment requests."""
    rows = (
        EquipmentRequest.query.filter_by(userId=current_user_id())
        .order_by(EquipmentRequest.created_at.desc())
        .all()
    )
    return jsonify(requests=[r.to_dict() for r in rows])
