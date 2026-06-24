from extensions import db
from models import Resource

def validate_resource_data(data):
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
    
def create_resource(form_data):
        """Handles Normal Flow: Create Resource."""
        # 1. Validation (E1)
        if not validate_resource_data(form_data):
            raise ValueError("Invalid Resource Details, please try again")
            
        # 2. Duplicate Check (NFR)
        if is_duplicate(form_data.get('name'), form_data.get('location')):
            raise ValueError("A resource with this name already exists at this location.")

        new_resource = Resource(
            name=form_data.get('name').strip(),
            type=form_data.get('type'),
            capacity=int(form_data.get('capacity', 0)),
            location=form_data.get('location').strip(),
            status=form_data.get('status', 'Available'),
            description=form_data.get('description'),
            isSpecialised=bool(form_data.get('isSpecialised'))
        )
        db.session.add(new_resource)
        db.session.commit()
        return new_resource

def update_resource(resource_id, form_data):
        """Handles Alternative Flow A1: Modify Current Resource."""
        resource = Resource.query.get_or_404(resource_id)
        
        if not validate_resource_data(form_data):
            raise ValueError("Invalid Resource Details, please try again")
            
        if is_duplicate(form_data.get('name'), form_data.get('location'), exclude_id=resource_id):
            raise ValueError("Another resource with this name already exists at this location.")

        resource.name = form_data.get('name').strip()
        resource.type = form_data.get('type')
        resource.capacity = int(form_data.get('capacity', 0))
        resource.location = form_data.get('location').strip()
        resource.status = form_data.get('status')
        resource.description = form_data.get('description')
        resource.isSpecialised = bool(form_data.get('isSpecialised'))
        
        db.session.commit()
        return resource

def allocate_to_booking(resource_id, booking_id):
        """Handles Alternative Flow A3: Assign Resource to Booking."""
        resource = Resource.query.get_or_404(resource_id)
        
        # In a real app, you would query your Booking model here:
        # booking = Booking.query.get_or_404(booking_id)
        # if booking.status != "Approved": raise ValueError("Booking is not approved.")
        
        # Update the status of the resource to "In Use"
        resource.status = "In Use"
        
        # Here you would also update your link table or booking record:
        # booking.resource_id = resource.resourceId
        
        db.session.commit()
        return True