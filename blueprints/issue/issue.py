"""US07 Report Issues: students flag faulty/damaged resources to managers.
    UR08 Receive Report: resource manager receive resource report from students"""
from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
    current_user_id, current_role,
)
from models import IssueReport, Resource, Booking, User
from storage import save_upload, IMAGE_EXTS
from blueprints.booking.services import notify

issueBp = Blueprint("issue", __name__, url_prefix="/api/issue")

# Reporting an issue is for the people who use resources.
REPORTERS = ("student", "staff")
VIEWERS = ("manager", "admin")

@issueBp.get("")
@login_required
def list_issues():
    """Managers/admins see every report; reporters see their own."""
    q = IssueReport.query.order_by(IssueReport.created_at.desc())
    if current_role() not in ("manager", "admin"):
        q = q.filter_by(userId=current_user_id())
    return jsonify(reports=[r.to_dict() for r in q.all()])


@issueBp.post("")
@role_required(*REPORTERS)
def create_issue():
    """Record a fault report (multipart: resourceId, description, image)."""
    # Supports multipart (with image) or plain JSON.
    data = request.form if (request.form or request.files) else (request.get_json(silent=True) or {})

    description = (data.get("description") or "").strip()
    if not description:
        # US07 E1: missing issue description.
        abort(400, description="Please describe the issue before submitting.")

    resource = _lookup_resource(data.get("resourceId"))

    # Optional link back to the booking the issue was noticed during.
    booking_id = data.get("bookingId")
    booking = None
    if booking_id:
        try:
            booking = Booking.query.get(int(booking_id))
        except (TypeError, ValueError):
            booking = None
        if booking and booking.userId != current_user_id():
            booking = None  # never attach someone else's booking

    image = request.files.get("image") if request.files else None
    image_name = save_upload(image, IMAGE_EXTS)

    report = IssueReport(
        userId=current_user_id(),
        resourceId=resource.resourceId,
        bookingId=booking.bookingId if booking else None,
        description=description,
        imagePath=image_name,
        status="open",
    )
    db.session.add(report)
    db.session.flush()

    # Notify every resource manager / admin (US07: alert resource manager).
    for mgr in User.query.filter(User.role.in_(("manager", "admin"))).all():
        notify(mgr.userId, "New issue reported",
               f"{resource.name}: {description[:80]}", type="maintenance")
    notify(current_user_id(), "Issue report submitted",
           f"Your report for {resource.name} was sent to the resource manager.",
           type="info")
    db.session.commit()
    return jsonify(report=report.to_dict()), 201


def _lookup_resource(resource_id):
    try:
        resource = Resource.query.get(int(resource_id)) if resource_id else None
    except (TypeError, ValueError):
        resource = None
    if not resource:
        abort(404, description="Resource not found.")
    return resource
