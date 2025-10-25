from app.extensions import db


class User(db.Model):
    """
    Represents a system user (manager or employee).
    Each user can belong to multiple companies and have multiple assignments, availabilities, and swaps.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True)
    hash = db.Column(db.String)  
    active = db.Column(db.Boolean, default=True, nullable=False)

    # Soft delete field — used for marking inactive or deleted users
    deleted_at = db.Column(db.DateTime)

    # Relationships with other models
    company_memberships = db.relationship(
        'CompanyUser',
        back_populates='user',
        cascade='save-update, merge'
    )

    shift_assignments = db.relationship(
        'ShiftAssignment',
        back_populates='user',
        passive_deletes=True
    )

    availabilities = db.relationship(
        'Availability',
        back_populates='user',
        passive_deletes=True
    )

    requested_swaps = db.relationship(
        'Swap',
        foreign_keys='Swap.requester_id',
        back_populates='requester'
    )

    responded_swaps = db.relationship(
        'Swap',
        foreign_keys='Swap.responder_id',
        back_populates='responder'
    )

    def __repr__(self):
        """Readable string representation for debugging."""
        return f"<User id={self.id} username={self.username} active={self.active}>"
