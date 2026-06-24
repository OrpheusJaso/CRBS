from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
    current_user_id,
)
from models import Equipment, EquipmentRequest
from datetime import datetime

equipmentManageBp = Blueprint("equipment", __name__, url_prefix="/api/equipment/manage")

# Resource Manager manages the equipment
MODIFIERS = ("manager",)

@equipmentManageBp.get("")
@login_required
def list_equipment():
    """Catalogue of equipment (drop-down options for the request form)."""
    return jsonify(equipment=[e.to_dict() for e in Equipment.query.all()])


@equipmentManageBp.post("")
@role_required(*MODIFIERS)
def create():
    """Create an Equipment (Equipment modal -> Create Equipment)."""
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
    
    if Equipment.query.filter_by(name=name).first():
        abort(409, description=f"A resource named '{name}' already exists.")
    
    equipment = Equipment(
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

@equipmentManageBp.put("/<int:equipment_id>")
@role_required(*MODIFIERS)
def modify_resource(equipment_id):
    """Modify Resource Details. Blocked inside the 24-hour window."""
    resource = Equipment.query.get_or_404(equipment_id)
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

@equipmentManageBp.delete("/<int:equipment_id>")
@role_required(*MODIFIERS)
def delete_resource(equipment_id):
    resource = Equipment.query.get_or_404(equipment_id)
    db.session.delete(resource)
    db.session.commit()
    return jsonify(message="Resource has been deleted.")