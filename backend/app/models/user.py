from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    hash = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text('true'))

    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now(), nullable=False)

    company_memberships = db.relationship('CompanyUser', back_populates='user', cascade='save-update, merge', lazy='selectin')

    shift_assignments = db.relationship(
        'ShiftAssignment',
        back_populates='user',
        passive_deletes=True,
        lazy='selectin',
        foreign_keys='ShiftAssignment.user_id'
    )

    requested_swaps = db.relationship(
        'Swap',
        foreign_keys='Swap.requester_id',
        back_populates='requester',
        lazy='selectin'
    )

    responded_swaps = db.relationship(
        'Swap',
        foreign_keys='Swap.responder_id',
        back_populates='responder',
        lazy='selectin'
    )

    approved_swaps = db.relationship(
        'Swap',
        foreign_keys='Swap.approved_by',
        back_populates='approver',
        lazy='selectin'
    )

    availabilities = db.relationship(
        'Availability',
        back_populates='user',
        passive_deletes=True,
        lazy='selectin',
        foreign_keys='Availability.user_id'
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username} active={self.active}>"