from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from sqlalchemy import CheckConstraint

class Leave(BaseModel):
    __tablename__ = 'leaves'
    company_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('companies.id', ondelete='RESTRICT'),
        nullable=False
    )

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False
    )

    status = db.Column(db.String(32), nullable=False, default="pending")
    
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)

    # "sick", "annual", "personal"
    type = db.Column(db.String(32), nullable=False)

    reason = db.Column(db.Text, nullable=True)
    reject_reason = db.Column(db.Text, nullable=True)
    # TODO: Currently supports a single approver.
    # Multi-level or multi-approver workflows can be considered in the future if needed.
    reviewed_by = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "type IN ('sick', 'annual', 'personal')",
            name="ck_leave_type"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'withdrawn')",
            name="ck_leave_status"
        ),
        CheckConstraint(
            """
            (status = 'rejected' AND reject_reason IS NOT NULL)
            OR
            (status != 'rejected' AND reject_reason IS NULL)
            """,
            name="ck_reject_reason_required"
        ),
        CheckConstraint(
            """
            (status IN ('approved', 'rejected') AND reviewed_at IS NOT NULL)
            OR
            (status IN ('pending', 'withdrawn') AND reviewed_at IS NULL)
            """,
            name="ck_approval_consistency"
        ),
        CheckConstraint(
            "start_at <= end_at",
            name="ck_leave_range_valid"
        ),
    )