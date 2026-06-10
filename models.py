from extensions import SQLAlchemy, db, datetime, timezone

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

    userId     = db.Column("userId", db.String(50), primary_key=True, unique = True, nullable = False, required = True)
    name       = db.Column("name", db.String(100), nullable = False, required = True)
    email      = db.Column("email", db.String(100), nullable = False, required = True)
    password   = db.Column("password", db.String(255), nullable = False, required = True)
    
    def __init__(self, userId, name, email, password):
        self.userId = userId
        self.name = name
        self.email = email
        self.password = password