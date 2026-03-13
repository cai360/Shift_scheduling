from app.models.companies import Company
from app.models.user import User
from app.extensions import db
from app.models.companies_users import CompanyUser 
from sqlalchemy.orm import selectinload
from app.services.company_service import CompanyService


class CompanyUserService:
    @staticmethod
    def get_active_membership(*, company_id, user_id):
        return CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.user_id == user_id,
            CompanyUser.deleted_at.is_(None)
        ).first()
    
    @staticmethod
    def get_members(*, company_id, user_id):
        # if user belong in company
        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=user_id
        )

        if not membership:
            raise PermissionError("Only company members can view members")
        
        return CompanyUser.query.options(selectinload(CompanyUser.user)).filter(
            CompanyUser.company_id == company_id,
            CompanyUser.deleted_at.is_(None)
        ).all()
    
    @staticmethod
    def join_company(company_id, user_id):
        """MVP: Only creator is owner. Everyone else is member."""
        CompanyService.get_company(company_id)

        # Is active membership or not
        existing = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.user_id == user_id,
            CompanyUser.deleted_at.is_(None)
        ).first()

        if existing:
            return existing

        # Previously deleted -> restore
        soft_deleted = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.user_id == user_id,
            CompanyUser.deleted_at.is_not(None)
        ).first()

        if soft_deleted:
            soft_deleted.deleted_at = None
            soft_deleted.role = "employee"
            db.session.commit()
            return soft_deleted

        # First time join
        company_user = CompanyUser(
            company_id=company_id,
            user_id=user_id,
            role="employee"
        )
        db.session.add(company_user)
        db.session.commit()
        return company_user

    

        
