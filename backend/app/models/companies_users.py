from app.extensions import db
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
    #  automatically delete related records if user/company is hard deleted
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey("users.id", 
                        ondelete="CASCADE"),
                        nullable=False)
    
    company_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey("companies.id", 
                           ondelete="CASCADE"),
                           nullable=False)

    # Role within the company (e.g., manager or employee)
    role = db.Column(db.String(32), 
                     nullable=False, 
                     default="employee")

    # NULL = active membership
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.CheckConstraint( "role IN ('manager','employee')",name="ck_company_users_role"),
                # partial unique index → one active membership per company
        db.Index(
            "uq_company_user_active",
            "company_id",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL")#把一段純 SQL 字串包成可被 SQLAlchemy 理解的 SQL 物件
        ),
    )


   
 