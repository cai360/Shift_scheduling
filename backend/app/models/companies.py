from app.extensions import db
from .base import BaseModel
from sqlalchemy import text

class Company(BaseModel):
    __tablename__ = 'companies'

    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable= False, default=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    company_users = db.relationship(
        "CompanyUser",
        back_populates="company",
        lazy="selectin"
    )
    
    __table_args__ = (
        db.Index(
            "uq_companies_name_active",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL")
        ),
    )

   