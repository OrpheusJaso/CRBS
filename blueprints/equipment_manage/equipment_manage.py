from extensions import (
    Blueprint, request, jsonify, abort, db, login_required, role_required,
    current_user_id,
)
from models import Equipment

equipmentManageBp = Blueprint("equipment_manage", __name__, url_prefix="/api/equipment/manage")

# Resource Manager manages the equipment
MODIFIERS = ("manager",)

@equipmentManageBp.get("")
@login_required
def list_equipment():
    """Catalogue of equipment (drop-down options for the request form)."""
    return jsonify(equipment=[eq.to_dict() for eq in Equipment.query.all()])


@equipmentManageBp.post("")
@role_required(*MODIFIERS)
def create():
    """Create an Equipment (Equipment modal -> Create Equipment)."""
    data = request.get_json(silent=True) or {}
    
    name = data.get("name", "").strip()
    resourceId = data.get("resourceId", "")
    type = data.get("type", "").strip()

    if not name:
        abort(400, description="Equipment name is required.")
    if not resourceId:
        abort(400, description="Equipment's associated Resource ID is required.")
    if not type:
        abort(400, description="Equipment type is required.")
    
    if Equipment.query.filter_by(name=name).first():
        abort(409, description=f"A equipment named '{name}' already exists.")
    
    equipment = Equipment(
        name=name,
        resourceId=resourceId,
        type=type,
        quantity=int(data.get("quantity", 0)),
        condition=data.get("condition", "available"),
        isSpecialised=bool(data.get("isSpecialised", False)),
    )
    db.session.add(equipment)
    db.session.commit()

    return jsonify(equipment=equipment.to_dict()), 201

@equipmentManageBp.put("/<int:equipment_id>")
@role_required(*MODIFIERS)
def modify_resource(equipment_id):
    """Modify Resource Details. Blocked inside the 24-hour window."""
    equipment = Equipment.query.get_or_404(equipment_id)
    data = request.get_json(silent=True) or {}

    if "name" in data:
        equipment.name = data["name"]
    if "type" in data:
        equipment.type = data["type"]
    if "resourceId" in data:
        equipment.resourceId = data["resourceId"]
    if "quantity" in data:
        equipment.quantity = data["quantity"]
    if "condition" in data:
        equipment.condition = data["condition"]
    if "isSpecialised" in data:
        equipment.isSpecialised = data["isSpecialised"]
        
    db.session.commit()
    return jsonify(equipment=equipment.to_dict())

@equipmentManageBp.delete("/<int:equipment_id>")
@role_required(*MODIFIERS)
def delete_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    db.session.delete(equipment)
    db.session.commit()
    return jsonify(message="Equipment has been deleted.")