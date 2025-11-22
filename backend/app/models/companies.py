from app.extensions import db
from datetime import datetime

class Company(db.Model):
    """
    Represents an organization (company or team) that can have multiple users, shifts, and schedules.
    Supports soft delete via `is_active` and `deleted_at`.
    """
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    require_swap_approval = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text('true')  
    )
    is_active = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text('true')
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=db.func.now(),
        server_default=db.func.now(),
        nullable=False
    )

    members = db.relationship(
        'CompanyUser',
        back_populates='company',
        cascade='save-update, merge',
        lazy='selectin'
    )

    availabilities = db.relationship(
        'Availability',
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    shifts = db.relationship(
        'Shift',
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    schedules = db.relationship(
        'Schedule',
        back_populates='company',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    swaps = db.relationship(
        'Swap',
        back_populates='company',
        cascade='all, delete-orphan',
        passive_deletes=True,
        lazy='selectin',
        foreign_keys='Swap.company_id' 
    )

    def deactivate(self):
        """Soft delete the company and deactivate all members."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
        for member in self.members:
            member.is_active = False