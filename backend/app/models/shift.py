from app.extensions import db
from sqlalchemy import UniqueConstraint

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('date', 'start_time', 'end_time', name='uq_shift_time'),
    )

    assignments = db.relationship('ShiftAssignment', back_populates='shift') 
    db.Index('ix_shift_date', 'date') 

    def __repr__(self):
        return f'<Shift {self.id} from {self.start_time} to {self.end_time} has capacity {self.capacity}>'