from app.extensions import db
from datetime import datetime

class Company(db.Model):
    """
    Represents an organization (e.g. company or team) that can have multiple users, shifts, and availabilities.
    Supports soft delete via `is_active` and `deleted_at`.
    """
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now())

    members = db.relationship('CompanyUser', back_populates='company', cascade='save-update, merge')
    
    availabilities = db.relationship('Availability', back_populates='company', cascade='all, delete-orphan')
    shifts = db.relationship('Shift', back_populates='company', cascade='all, delete-orphan')

    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime)


    def deactivate(self):
        """Soft delete the company and deactivate all members."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
        for member in self.members:
            member.is_active = False
