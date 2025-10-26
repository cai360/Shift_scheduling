from app.extensions import db
from sqlalchemy import UniqueConstraint, func
from datetime import datetime, timedelta

class Shift(db.Model):
    """
    Represents a work shift within a specific company and schedule period.
    Each shift has a date, start and end time, capacity, and calculated duration.
    """
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    schedule_id = db.Column(
        db.Integer,
        db.ForeignKey('schedules.id', ondelete='SET NULL'),
        nullable=True
    )

    date = db.Column(db.Date, nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=True)

    # Duration (in minutes)
    duration = db.Column(db.Integer, nullable=True)

    # Soft delete + timestamps
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now(), nullable=False)

    # Relationships
    company = db.relationship('Company', back_populates='shifts')
    schedule = db.relationship('Schedule', back_populates='shifts')

    assignments = db.relationship(
        'ShiftAssignment',
        back_populates='shift',
        cascade='all, delete-orphan'
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'date', 'starting_time', 'ending_time', name='uq_company_shift_time'),
        db.Index('ix_shift_date', 'date'),
    )

    # --- Methods ---
    def calculate_duration(self):
        """Calculate duration in minutes from starting_time and ending_time."""
        if self.starting_time and self.ending_time:
            start_dt = datetime.combine(datetime.today(), self.starting_time)
            end_dt = datetime.combine(datetime.today(), self.ending_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)  # handle overnight shifts
            self.duration = int((end_dt - start_dt).total_seconds() / 60)
        return self.duration

    def __repr__(self):
        """Readable string representation for debugging."""
        return (
            f"<Shift id={self.id} "
            f"date={self.date} "
            f"{self.starting_time}-{self.ending_time} "
            f"cap={self.capacity}>"
        )