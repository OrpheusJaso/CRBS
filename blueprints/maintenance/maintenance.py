from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
    current_user_id,
)
from models import Maintenance, Resource, MaintenanceLog
from blueprints.maintenance.services import has_conflict, notify_all, edit_resource_status
from datetime import datetime

maintenanceBp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")

# Specialised equipment requests come from staff (and admins acting as staff).
MODIFIERS = ("manager", "admin")

@maintenanceBp.get("")
@login_required
def list_maintenance():
    """Catalogue of maintenances."""
    return jsonify(maintenance=[m.to_dict() for m in Maintenance.query.all()])

@maintenanceBp.get("/active")
@login_required
def list_active_maintenance():
    """Resources currently under maintenance (drop-down option for maintenance completion form)."""
    records = (
        Maintenance.query
        .filter(Maintenance.status.in_(["scheduled"]))
        .all()
    )
    return jsonify(maintenance=[m.to_dict() for m in records])

@maintenanceBp.get("/resources")
@login_required
def list_resource():
    """Catalogue of resource (drop-down options for the maintenance form)."""
    return jsonify(resource=[r.to_dict() for r in Resource.query.all()])

@maintenanceBp.post("/create")
@role_required(*MODIFIERS)
def create_maintenance():
    """Submit a resource to be under maintenance (Resource Maintenance form)."""
    
    data = request.get_json(silent=True) or {}
    name = (data.get("resourceName") or "").strip()
    if not name:
        abort(400, description="'resourceName' is required.")
        
    resource = Resource.query.filter_by(name=name).first()
    
    duration = (data.get("duration") or "")
    
    completion_date = None
    if data.get("completionDate"):
        try:
            completion_date = datetime.fromisoformat(data["completionDate"])
        except ValueError:
            abort(400, description="Invalid 'completionDate'.")

    if has_conflict(resource.resourceId, datetime.now(), completion_date):
        abort(409, description=f"'{name}' already has an overlapping maintenance window.")

    maintenance = Maintenance(
        resourceId = resource.resourceId,
        description = data.get("description"),
        scheduledDate = datetime.now(),
        completedDate = completion_date,
        duration = duration,
        status = "scheduled",
    )
    db.session.add(maintenance)
    db.session.commit()
    
    edit_resource_status(resource.resourceId, "maintenance")
    
    notify_all(
    "Resource under maintenance",
    f"{name} is now under maintenance and unavailable for booking.",
    type="maintenance",
    )
    
    return jsonify(maintenance=maintenance.to_dict()), 201

@maintenanceBp.post("/<int:maintenance_id>/complete")
@role_required(*MODIFIERS)
def complete_maintenance(maintenance_id):
    """Complete a Resource Maintenance (Complete Maintenance form)."""
    
    m = Maintenance.query.filter_by(maintenanceId=maintenance_id).first()
    if not m:
        abort(404, description="Maintenance record not found.")
    
    m.status = "completed"
    m.completedDate = datetime.now()
    
    try:
        edit_resource_status(m.resourceId, "available")
    except ValueError as e:
        abort(400, description=str(e))
    
    notify_all(
    "Resource completed maintenance",
    f"{m.resource.name if m.resource else 'A resource'} has completed maintenance and available for booking.",
    type="maintenance",
    )
    
    return jsonify(maintenance=m.to_dict()), 201
