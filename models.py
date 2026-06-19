from extensions import SQLAlchemy, db, datetime, psycopg2, os, Flask
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASS']}"
    f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', 5432)}/{os.environ['DB_NAME']}"
)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("Database connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")

class timestampMixin:
    """Adds created_at and updated_at to any model."""
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
    )

# For the Tables of the Databaes
class User(db.Model):
    __tablename__ = 'User'

    userId     = db.Column("userId", db.String(50), primary_key=True, unique = True, nullable = False)
    name       = db.Column("name", db.String(100), nullable = False)
    email      = db.Column("email", db.String(100), nullable = False)
    password   = db.Column("password", db.String(255), nullable = False)
    
    def __init__(self, userId, name, email, password):
        self.userId = userId
        self.name = name
        self.email = email
        self.password = password
        
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