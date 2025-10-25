from app.extensions import db

class ShiftAssignment(db.Model):
    """
    Represents an assignment of a user (employee) to a specific shift.
    Each record connects one user to one shift and can be used for swap requests.
    """
    __tablename__ = 'shift_assignments'

    id = db.Column(db.Integer, primary_key=True)


    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    shift_id = db.Column(
        db.Integer,
        db.ForeignKey('shifts.id', ondelete='CASCADE'),
        nullable=False
    )

    user = db.relationship(
        'User',
        back_populates='shift_assignments',
        passive_deletes=True
    )

    shift = db.relationship(
        'Shift',
        back_populates='assignments'
    )

    swaps = db.relationship(
        'Swap',
        back_populates='shift_assignment',
        cascade='all, delete-orphan'
    )

    # Prevent duplicate assignments for the same user and shift
    __table_args__ = (
        db.UniqueConstraint('shift_id', 'user_id', name='uq_shift_user_unique'),
    )
