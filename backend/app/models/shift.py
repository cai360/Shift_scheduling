from app.extensions import db
from sqlalchemy import UniqueConstraint, func, text
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

    capacity = db.Column(db.Integer, nullable=False)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)

    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.CheckConstraint(
            'end_at > start_at',
            name='ck_shift_time_order'
        ),
        db.Index('ix_shift_start_at', 'start_at'),
        db.Index('ix_shift_end_at', 'end_at'),
        db.Index(
            'uq_shift_company_slot',
            'company_id', 'start_at', 'end_at',
            unique=True,
            postgresql_where=text('deleted_at IS NULL'),
        ),
    )

    assignments = db.relationship(
        "ShiftAssignment",
        back_populates="shift",
        lazy="selectin",
        primaryjoin=(
            "and_("
            "ShiftAssignment.shift_id == Shift.id, "
            "ShiftAssignment.deleted_at.is_(None)"
            ")"
        ),
        passive_deletes=True,
    )


    @hybrid_property
    def duration_minutes(self):
        return int((self.end_at - self.start_at).total_seconds() / 60)

    
