from app.extensions import db
from sqlalchemy import UniqueConstraint

class Shift(db.Model):
    """
    Represents a work shift within a specific company.
    Each shift has a date, start and end time, and capacity (number of available positions).
    """
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )


    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)   # Only stores HH:MM
    end_time = db.Column(db.Time, nullable=False)     # Only stores HH:MM
    capacity = db.Column(db.Integer, nullable=False)

    company = db.relationship('Company', back_populates='shifts')
    assignments = db.relationship(
        'ShiftAssignment',
        back_populates='shift',
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        # Prevent duplicate shifts with the same company/date/time combination
        UniqueConstraint('company_id', 'date', 'start_time', 'end_time', name='uq_company_shift_time'),
        db.Index('ix_shift_date', 'date'),
    )

    def __repr__(self):
        """Readable string representation for debugging."""
        return f"<Shift id={self.id} date={self.date} {self.start_time}-{self.end_time} cap={self.capacity}>"
