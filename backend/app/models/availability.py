from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class Availability(BaseModel):
    __tablename__ = 'availabilities'

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    company_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            'company_id', 
            'user_id', 
            'date', 
            'starting_time', 
            'ending_time',
            name='uq_company_user_availability'
        ),
    )

