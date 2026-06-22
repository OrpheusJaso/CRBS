from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
)
from models import Resource, Booking
from datetime import datetime
from blueprints.booking.services import has_conflict, parse_dt

resourceBp = Blueprint("resource", __name__, url_prefix="/api/resource")

# Searching/booking is for students and staff (matches the UI sidebar roles).
SEARCHERS = ("student", "staff")


@resourceBp.get("")
@login_required
def list_resources():
    """Return every resource (no filtering)."""
    return jsonify(resources=[r.to_dict() for r in Resource.query.all()])


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
            available = r.status == "available" and not has_conflict(
                r.resourceId, start, end
            )
            item["available"] = available
        else:
            item["available"] = r.status == "available"
        results.append(item)

    return jsonify(count=len(results), resources=results)
