from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class Unavailability(BaseModel):
    __tablename__ = 'unavailabilities'

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

    starting_time = db.Column(db.DateTime, nullable=False)
    ending_time = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            'company_id', 
            'user_id', 
            'starting_time', 
            'ending_time',
            name='uq_company_user_unavailability'
        ),
    )

