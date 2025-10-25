from app.extensions import db

class Swap(db.Model):
    """
    Represents a shift swap request between employees.
    Each swap belongs to a shift assignment and involves a requester and (optionally) a responder.
    The manager can later approve or deny the swap.
    """
    __tablename__ = 'swaps'

    id = db.Column(db.Integer, primary_key=True)

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey('shift_assignments.id', ondelete='CASCADE'),
        nullable=False
    )

    requester_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=False
    )

    responder_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    cancelled = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'approved', or 'denied'

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    shift_assignment = db.relationship(
        'ShiftAssignment',
        back_populates='swaps'
    )

    requester = db.relationship(
        'User',
        foreign_keys=[requester_id],
        back_populates='requested_swaps',
        overlaps="responder,responded_swaps"
    )

    responder = db.relationship(
        'User',
        foreign_keys=[responder_id],
        back_populates='responded_swaps',
        overlaps="requester,requested_swaps"
    )

    def __repr__(self):
        """Readable string representation for debugging."""
        return f"<Swap id={self.id} status={self.status} cancelled={self.cancelled}>"
