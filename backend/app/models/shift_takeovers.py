from app.extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from sqlalchemy.sql import func 

class ShiftTakeover(BaseModel):
    __tablename__ = 'shift_takeovers'

    company_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    assignment_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('shift_assignments.id', ondelete='CASCADE'),
        nullable=False
    )

    requester_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    responder_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    respond_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    approved_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'),
                nullable=True)
    
    approved_at = db.Column(db.DateTime(timezone=True))

    status = db.Column(db.String(32), nullable=False, default="pending")

    __table_args__ = (
        db.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'cancelled')", name="ck_shift_takeover_status"),

        db.Index(
            "uq_takeover_assignment_pending",
            "assignment_id",
            unique=True,
            postgresql_where=db.text("status = 'pending'")
        )
    )
