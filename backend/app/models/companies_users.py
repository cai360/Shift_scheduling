from app.extensions import db
from datetime import datetime

class CompanyUser(db.Model):
    """
    Association table linking users and companies.
    Supports soft deletion (is_active, left_at) to track join and leave history.
    """
    __tablename__ = 'company_users'

    id = db.Column(db.Integer, primary_key=True)

    #  automatically delete related records if user/company is hard deleted
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    # Role within the company (e.g., manager or employee)
    role = db.Column(db.String(20), nullable=False)

    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    left_at = db.Column(db.DateTime)

    # Soft delete flag — mark inactive instead of deleting the record
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='company_memberships')
    company = db.relationship('Company', back_populates='members')

    # Ensure a user can only have one record per company
    __table_args__ = (
        db.UniqueConstraint('company_id', 'user_id', name='uq_company_user_unique'),
    )

    def deactivate(self):
        """Mark this membership as inactive and set the leave timestamp."""
        self.is_active = False
        self.left_at = datetime.utcnow()
