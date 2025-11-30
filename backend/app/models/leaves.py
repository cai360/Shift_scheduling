from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from sqlalchemy import CheckConstraint

class Leave(BaseModel):
    __tablename__ = 'leaves'
    company_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True
    )
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    # "sick", "annual", "personal"
    type = db.Column(db.String(32), nullable=False)

    approved_by = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    approved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'withdrawn')",
            name="ck_leave_status"
        ),
        CheckConstraint(
            "start_date <= end_date",
            name="ck_leave_range_valid"
        ),
    )