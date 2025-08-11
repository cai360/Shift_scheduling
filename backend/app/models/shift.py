from app.extensions import db
from sqlalchemy import UniqueConstraint

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)   # 只存 hh:mm
    end_time = db.Column(db.Time, nullable=False)     # 只存 hh:mm
    capacity = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('date', 'start_time', 'end_time', name='uq_shift_time'),
        db.Index('ix_shift_date', 'date'),
    )

    assignments = db.relationship('ShiftAssignment', back_populates='shift')

    def __repr__(self):
        return f'<Shift {self.id} {self.date} {self.start_time}-{self.end_time} cap={self.capacity}>'