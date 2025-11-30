from app.extensions import db
from sqlalchemy import UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
from .base import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property

class Shift(BaseModel):
    __tablename__ = 'shifts'

    company_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    schedule_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('schedules.id', ondelete='SET NULL'),
        nullable=True
    )

    date = db.Column(db.Date, nullable=False)

    capacity = db.Column(db.Integer, nullable=True)

    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    #temporary limited same starting_time and same ending_time can't exit in the same day
    __table_args__ = (
        UniqueConstraint(
            'company_id',
            'date',
            'starting_time',
            'ending_time',
            name='uq_company_shift_time'
        ),
        db.Index('ix_shift_date', 'date'),
    )


    #calculate the duration 
    @hybrid_property 
    def duration(self):
        if not self.starting_time or not self.ending_time:
            return None
        start_dt = datetime.combine(datetime.today(), self.starting_time)
        end_dt = datetime.combine(datetime.today(), self.ending_time)
        # Overnight
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        # Return minutes
        return int((end_dt - start_dt).total_seconds() / 60)


    
