from app.models.companies import Company
from app.models.user import User
from app.extensions import db
from app.models.companies_users import CompanyUser 
from sqlalchemy.orm import selectinload

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
