from app.extensions import db
from sqlalchemy import UniqueConstraint, func
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class ShiftAssignment(BaseModel):
    __tablename__ = 'shift_assignments'

    # FK → leave empty if user deleted
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    shift_id = db.Column(UUID(as_uuid=True), db.ForeignKey('shifts.id', ondelete='CASCADE'), nullable=False)

    assigned_by = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'),
                nullable=True)
    
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # TODO:
    # This unique constraint is temporary.
    # It should be replaced by a partial unique index
    # (user_id, shift_id) WHERE deleted_at IS NULL,
    # enforced at the database level via a migration.

   