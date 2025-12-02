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
    
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'shift_id',
            name='uq_user_shift_assignments'
        ),
    )

   