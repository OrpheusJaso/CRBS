from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required, render_template
)
from models import Resource, Booking
from datetime import datetime
from blueprints.booking.services import parse_dt, has_conflict
from .services import is_duplicate, validate_resource_data

resourceBp = Blueprint("resource", __name__, url_prefix="/api/resource")

# Searching/booking is for students and staff (matches the UI sidebar roles).
SEARCHERS = ("student", "staff")
MODIFIERS = ("manager",)

@resourceBp.get("")
@login_required
def list_bookings():
    """Return the signed-in user's resources (the Manage Resources table)."""
    rows = Resource.query.all()
    return jsonify(resources=[r.to_dict() for r in rows])

@resourceBp.get("/search")
@role_required(*SEARCHERS)
def search():
    """Search & Book filter: type, date, start/end time, capacity.

    Query params (all optional):
      type=meeting room|computer lab|projector|...
      capacity=30
      date=2026-06-09  start=10:00  end=12:00   (availability check)
    """
    q = Resource.query
    rtype = request.args.get("type")
    if rtype and rtype.lower() not in ("all", "all resources"):
        q = q.filter(db.func.lower(Resource.type) == rtype.lower())

    capacity = request.args.get("capacity", type=int)
    if capacity:
        q = q.filter(Resource.capacity >= capacity)

    location = request.args.get("location")
    if location:
        q = q.filter(Resource.location.ilike(f"%{location.strip()}%"))

    candidates = q.all()

    # If a date/time window is given, compute availability per resource.
    start = end = None
    date = request.args.get("date")
    if date and request.args.get("start"):
        try:
            start = parse_dt(f"{date}T{request.args['start']}")
            end_str = request.args.get("end") or request.args["start"]
            end = parse_dt(f"{date}T{end_str}")
            if end <= start:
                end = None
        except ValueError:
            abort(400, description="Invalid date/time in search.")

    results = []
    for r in candidates:
        item = r.to_dict()
        if start and end:
            # Availability = bookable status AND no overlapping active booking.
            available = r.status == "available" and not has_conflict(
                r.resourceId, start, end
            )
            item["available"] = available
        else:
            item["available"] = r.status == "available"
        results.append(item)

    return jsonify(count=len(results), resources=results)

@resourceBp.post("")
@role_required(*MODIFIERS)
def create():
    """Create a resource (Resource modal -> Create Resource)."""
    data = request.get_json(silent=True) or {}
    
    name = data.get("name", "").strip()
    type = data.get("type", "").strip()
    location = data.get("location", "").strip()

    if not name:
        abort(400, description="Resource name is required.")
    if not type:
        abort(400, description="Resource type is required.")
    if not location:
        abort(400, description="Location is required.")
    
    if Resource.query.filter_by(name=name).first():
        abort(409, description=f"A resource named '{name}' already exists.")
    
    resource = Resource(
        name=name,
        type=type,
        capacity=int(data.get("capacity", 0)),
        location=location,
        status=data.get("status", "available"),
        description=data.get("description", "").strip() or None,
        isSpecialised=bool(data.get("isSpecialised", False)),
    )
    db.session.add(resource)
    db.session.commit()

    return jsonify(resource=resource.to_dict()), 201

@resourceBp.put("/<int:resource_id>")
@role_required(*MODIFIERS)
def modify_resource(resource_id):
    """Modify Resource Details. Blocked inside the 24-hour window."""
    resource = Resource.query.get_or_404(resource_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        resource.name = data["name"]
    if "type" in data:
        resource.type = data["type"]
    if "capacity" in data:
        resource.capacity = data["capacity"]
    if "location" in data:
        resource.location = data["location"]
    if "status" in data:
        resource.status = data["status"]
    if "description" in data:
        resource.description = data["description"]
    if "isSpecialised" in data:
        resource.isSpecialised = data["isSpecialised"]
        
    db.session.commit()
    return jsonify(resource=resource.to_dict())

@resourceBp.delete("/<int:resource_id>")
@role_required(*MODIFIERS)
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    return jsonify(message="Resource has been deleted.")