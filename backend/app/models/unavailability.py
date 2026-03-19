from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from sqlalchemy import text


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

    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.Index(
            'uq_company_user_unavailability_active',
            'company_id',
            'user_id',
            'start_at',
            'end_at',
            unique=True,
            postgresql_where=text('deleted_at IS NULL')
        ),
    )

