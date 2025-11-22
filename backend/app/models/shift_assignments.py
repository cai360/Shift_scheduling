from app.extensions import db


class ShiftAssignment(db.Model):
    __tablename__ = 'shift_assignments'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shifts.id', ondelete='CASCADE'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now(), nullable=False)

    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        back_populates='shift_assignments',
        lazy='selectin',
        overlaps="updated_by_user"
    )

    updated_by_user = db.relationship(
        'User',
        foreign_keys=[updated_by],
        lazy='selectin',
        overlaps="user,shift_assignments"
    )

    shift = db.relationship('Shift', back_populates='assignments', lazy='selectin')

    swaps = db.relationship('Swap', back_populates='shift_assignment', cascade='all, delete-orphan', lazy='selectin')

    __table_args__ = (
        db.UniqueConstraint('shift_id', 'user_id', name='uq_shift_user_unique'),
    )

    def __repr__(self):
        return f"<ShiftAssignment id={self.id} user_id={self.user_id} shift_id={self.shift_id}>"