from extensions import db
from models import Resource, Equipment

def validate_equipment_data(data):
        """Satisfies E1: Validates details before saving."""
        name = data.get('name')
        capacity = data.get('capacity')
        
        # Simple validation check
        if not name or str(name).strip() == "":
            return False
        try:
            if int(capacity) < 0:
                return False
        except (ValueError, TypeError):
            return False
            
        return True

def is_duplicate(name, location, exclude_id=None):
        """Satisfies NFR: Prevents duplicate resources in the same location."""
        query = Resource.query.filter(
            Resource.name.ilike(name.strip()),
            Resource.location.ilike(location.strip())  
        )
        if exclude_id:
            query = query.filter(Resource.resourceId != exclude_id)
        
        return query.first() is not None
    
def create_equipment(form_data):
        """Handles Normal Flow: Create Resource."""
        # 1. Validation (E1)
        if not validate_equipment_data(form_data):
            raise ValueError("Invalid Equipment Details, please try again")
            
        # 2. Duplicate Check (NFR)
        if is_duplicate(form_data.get('name'), form_data.get('location')):
            raise ValueError("An equipment with this name already exists at this location.")

        new_equipment = Equipment(
            name=form_data.get('name').strip(),
            type=form_data.get('type'),
            resourceId=int(form_data.get('resourceId', 0)),
            quantity=int(form_data.get('quantity', 0)),
            condition=form_data.get('condition', 'Good'),
            isSpecialised=bool(form_data.get('isSpecialised'))
        )
        db.session.add(new_equipment)
        db.session.commit()
        return new_equipment

def update_equipment(equipment_id, form_data):
        """Handles Alternative Flow A1: Modify Current Resource."""
        equipment = Equipment.query.get_or_404(equipment_id)
        
        if not validate_equipment_data(form_data):
            raise ValueError("Invalid Resource Details, please try again")
            
        if is_duplicate(form_data.get('name'), form_data.get('location'), exclude_id=equipment_id):
            raise ValueError("Another resource with this name already exists at this location.")

        equipment.name=form_data.get('name').strip(),
        equipment.type=form_data.get('type'),
        equipment.resourceId=int(form_data.get('resourceId', 0)),
        equipment.quantity=int(form_data.get('quantity', 0)),
        equipment.condition=form_data.get('condition', 'Good'),
        equipment.isSpecialised=bool(form_data.get('isSpecialised'))
        
        db.session.commit()
        return equipment