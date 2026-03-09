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
    
    @staticmethod
    def leave_company():
        ...

    @staticmethod
    def transfer_ownership(company_id, actor_user_id, target_user_id):
        if actor_user_id == target_user_id:
            raise ValueError("Cannot transfer ownership to the same user.")

        target = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=target_user_id
        )
        if not target:
            raise ValueError("Target user is not a company member")
        
        actor = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=actor_user_id
        )
        if not actor:
            raise ValueError("Actor is not a company member.")
        if actor.role != "owner":
            raise PermissionError("Only owner can transfer ownership.")
        if target.role == "owner":
            raise ValueError("Target user is already an owner.")

        try:
            actor.role = "manager"
            target.role = "owner"
            db.session.commit()
            return target
        except Exception:
            db.session.rollback()
            raise

    
    @staticmethod
    def count_active_members(company_id):
        count = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.deleted_at.is_(None)
        ).count
        return count

    @staticmethod
    def count_active_owners(company_id):
        count = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.role == "owner",
            CompanyUser.deleted_at.is_(None)
        ).count()
        return count

    

        
