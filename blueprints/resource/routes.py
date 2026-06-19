from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db

resourceBp = Blueprint("resource", __name__, url_prefix="/resource")

class Resource(db.Model):
    
    __tablename__ = "resource"
    
    resourceId = db.Column("resourceId",  db.Integer, db.Sequence('resourceId_seq', start=400), primary_key = True, nullable = False)
    name = db.Column("name", db.String(100), nullable = False)
    type = db.Column("type", db.String(50), nullable = False)
    capacity = db.Column("capacity", db.Integer, nullable = False)
    location = db.Column("location", db.String(255), nullable = False)
    status = db.Column("status", db.String(100), nullable = False)
    description = db.Column("description", db.String(255), nullable = True)
    isSpecialised = db.Column("isSpecialised", db.Boolean, nullable = False)
    
    def __init__(self, name, type, capacity, location, status, isSpecialised, description=None):
        self.name = name
        self.type = type
        self.capacity = capacity
        self.location = location
        self.status = status
        self.isSpecialised = isSpecialised
        self.description = description
        
# Getters
    def getResourceId(self):
        return self.__resourceId
    
    def getResourceName(self):
        return self.__name
    
    def getResourceType(self):
        return self.__type
    
    def getResourceCapacity(self):
        return self.__capacity
    
    def getResourceLocation(self):
        return self.__location
    
    def getResourceStatus(self):
        return self.__status
    
    def getResourceDescription(self):
        return self.__description
    
    def getResourceIsSpecialised(self):
        return self.__isSpecialised

# Setters        
    def setResourceId(self, resourceId):
        self.__resourceId = resourceId
    
    def setResourceName(self, name):
        self.__name = name
    
    def setResourceType(self, type):
        self.__type = type
    
    def setResourceCapacity(self, capacity):
        self.__capacity = capacity
    
    def setResourceLocation(self, location):
        self.__location = location
    
    def setResourceStatus(self, status):
        self.__status = status
    
    def setResourceDescription(self, description):
        self.__description = description
    
    def setResourceIsSpecialised(self, isSpecialised):
        self.__isSpecialised = isSpecialised

@resourceBp.route('/')
def index():
    """Read: Display the resource table."""
    return render_template('resource/index.html', view = 'table', resources="models.py")

@resourceBp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        new_resource = Resource(
            name=request.form.get('name'),
            type=request.form.get('type'),
            capacity=int(request.form.get('capacity', 0)),
            location=request.form.get('location'),
            status=request.form.get('status'),
            description=request.form.get('description'),
            isSpecialised=bool(request.form.get('isSpecialised'))
        )
        db.session.add(new_resource)
        db.session.commit()
        flash('Resource created successfully!')
        return redirect(url_for('resource.index'))
    
    return render_template('resource.html', view='form', action="Create", resource={})

@resourceBp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
def edit(resource_id):
    """Update: Display form view / handle update."""
    resource = Resource.query.get_or_404(resource_id)

    if request.method == 'POST':
        resource.name = request.form.get('name')
        resource.type = request.form.get('type')
        db.session.commit()
        flash('Resource updated successfully!')
        return redirect(url_for('resource.index'))

    return render_template('resource.html', view='form', action="Edit", resource=resource)

@resourceBp.route('/<int:resource_id>/delete', methods=['POST'])
def delete(resource_id):
    """Delete: Handle removal."""
    resource = Resource.query.get_or_404(resource_id)
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted successfully!')
    return redirect(url_for('resource.index'))