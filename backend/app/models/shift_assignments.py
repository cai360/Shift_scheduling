from app.extensions import db
from sqlalchemy import text
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class ShiftAssignment(BaseModel):
    __tablename__ = 'shift_assignments'

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    shift_id = db.Column(UUID(as_uuid=True), db.ForeignKey('shifts.id', ondelete='CASCADE'), nullable=False)

    assigned_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'),
                nullable=True)
    
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    shift = db.relationship(
        "Shift",
        back_populates="assignments"
    )

    __table_args__ = (
    db.Index(
        "uq_shift_assignment_active",
        "user_id",
        "shift_id",
        unique=True,
        postgresql_where=text("deleted_at IS NULL")
    ),
)

   