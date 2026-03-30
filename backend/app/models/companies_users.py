from app.extensions import db
from app.models import User
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
from .base import BaseModel

class CompanyUser(BaseModel):
    """
    Association table linking users and companies.
    Support one user and belong in multiple companies
    """
    __tablename__ = 'company_users'
    #  automatically delete related records if user/company is hard deleted, but user is Soft delete only in this system
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey("users.id"),
                        nullable=False)
    
    company_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey("companies.id", ondelete="CASCADE"),
                           nullable=False)

    # Role within the company (e.g., owner, manager or employee)
    role = db.Column(db.String(32), 
                     nullable=False, 
                     default="employee")

    # NULL = active membership
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    user = db.relationship(
        User,
        backref="company_memberships",
        lazy="select"
    )

    __table_args__ = (
        db.CheckConstraint( "role IN ('owner', 'manager','employee')",name="ck_company_users_role"),

        db.Index(
            "uq_company_user_active",
            "company_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL")
        ),
        db.Index(
            "uq_active_owner_per_company",
            "company_id",
            unique=True,
            postgresql_where=text("role = 'owner' AND deleted_at IS NULL")
        ),
    )


   
 