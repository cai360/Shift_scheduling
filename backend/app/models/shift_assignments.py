from app.extensions import db

class ShiftAssignment(db.Model):
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

    user  = db.relationship('User', back_populates='shift_assignments', passive_deletes=True)
    shift = db.relationship('Shift', back_populates='shift_assignments')