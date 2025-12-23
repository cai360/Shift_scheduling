from app.models.companies import Company
from app.extensions import db
from app.models.companies_users import CompanyUser   

class CompanyUserService:
    @staticmethod
    def get_active_membership(*, company_id, user_id):
        return CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.user_id == user_id,
            CompanyUser.deleted_at.is_(None)
<<<<<<< HEAD
        ).first()
    
    @staticmethod
    def require_manager(*, company_id, user_id):
        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=user_id
        )

        if not membership or membership.role != 'manager':
            raise PermissionError("Only manager allowed.")
        
        return membership
=======
        ).first()
>>>>>>> 4b0f1d0 (feat(shift):create_shift api)
