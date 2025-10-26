from app.extensions import db
from sqlalchemy import Enum


class Swap(db.Model):
    __tablename__ = 'swaps'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('shift_assignments.id', ondelete='CASCADE'))
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    ) 

    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    status = db.Column(
        Enum('pending', 'approved', 'rejected', name='swap_status'),
        nullable=False,
        server_default=db.text("'pending'")
    )

    cancelled = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now(), nullable=False)

    shift_assignment = db.relationship(
        'ShiftAssignment', 
        back_populates='swaps', 
        lazy='selectin')

    requester = db.relationship(
        'User',
        foreign_keys=[requester_id],
        back_populates='requested_swaps',
        lazy='selectin',
        overlaps="responder,responded_swaps,approver,approved_swaps"
    )

    responder = db.relationship(
        'User',
        foreign_keys=[responder_id],
        back_populates='responded_swaps',
        lazy='selectin',
        overlaps="requester,requested_swaps,approver,approved_swaps"
    )

    approver = db.relationship(
        'User',
        foreign_keys=[approved_by],
        back_populates='approved_swaps',
        lazy='selectin',
        overlaps="requester,responder,requested_swaps,responded_swaps"
    )

    company = db.relationship(
        'Company',
        back_populates='swaps',
        foreign_keys=[company_id]
    )

    def __repr__(self):
        return f"<Swap id={self.id} status={self.status}>"