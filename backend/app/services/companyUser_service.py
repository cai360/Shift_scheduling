from app.models.companies import Company
from app.models.user import User
from app.extensions import db
from app.models.companies_users import CompanyUser 
from sqlalchemy.orm import selectinload
from app.services.company_service import CompanyService
from datetime import datetime, timezone


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
        """MVP: Only creator is owner. Everyone else defult as member."""
        CompanyService.get_company(company_id)

        # Check if the user already has an active membership
        existing = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.user_id == user_id,
            CompanyUser.deleted_at.is_(None)
        ).first()

        # Idempotent
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
    def leave_company(company_id, user_id):
        """
        Business rules:
            - A company must always have exactly one active owner unless the company is deleted.
            - Non-owner members can leave directly.
            - The sole owner can leave only if they are the last active member, in which case the company is soft-deleted.
            - Otherwise, the owner must transfer ownership before leaving.
            - Before leaving, ensure all future assignments and takeovers have been resolved.
        TODO:
        Before leaving the company, ensure that all future assignments and takeovers have been resolved.
        """
        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id = user_id
        )
        if not membership:
            raise ValueError("User is not a company member")
        
        member_count = CompanyUserService.count_active_members(company_id)

        if membership.role != 'owner':
            membership.deleted_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        
        # owner is the last member -> delete company
        if member_count == 1:
            CompanyService.soft_delete_company(
                company_id=company_id,
                user_id=user_id
            )
            return True
        
        # owner cannot leave while company still has other active members
        raise ValueError(
            "Ownership must be transferred before leaving the company"
        )
        

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

        try:
            actor.role = "manager"
            target.role = "owner"
            CompanyUserService.validate_single_owner(company_id)

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
        ).count()
        return count

    @staticmethod
    def count_active_owners(company_id):
        count = CompanyUser.query.filter(
            CompanyUser.company_id == company_id,
            CompanyUser.role == "owner",
            CompanyUser.deleted_at.is_(None)
        ).count()
        return count
    
    @staticmethod
    def validate_single_owner(company_id):
        owner_count = CompanyUserService.count_active_owners(company_id)
        if owner_count != 1:
            raise RuntimeError(
            f"[Invariant Violation] company {company_id} has {owner_count} owners"
            )

    

        
