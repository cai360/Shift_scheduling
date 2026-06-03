from app.services.companyUser_service import CompanyUserService
from app.errors.error_base import PermissionDeniedError
from typing import Iterable
from werkzeug.exceptions import Forbidden

class PermissionService:
    @staticmethod
    def require_roles(*, company_id, user_id, allowed_roles:Iterable[str]):
        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=user_id
        )
        if not membership:
            raise PermissionDeniedError(message="Membership not found.")
        if membership.role not in allowed_roles:
            raise PermissionDeniedError(message="Permission denied.")
        return membership

    @staticmethod
    def require_can_manage_company(*, company_id, user_id):
        return PermissionService.require_roles(
            company_id=company_id,
            user_id=user_id,
            allowed_roles=("manager", "owner"),
        )
    
    @staticmethod
    def require_owner(*, company_id, user_id):
        return PermissionService.require_roles(
            company_id=company_id,
            user_id=user_id,
            allowed_roles=("owner",)
        )

    @staticmethod
    def require_active_member(*, company_id, user_id):
        return PermissionService.require_roles(
            company_id=company_id,
            user_id=user_id,
            allowed_roles=("employee", "manager", "owner")
        )
    @staticmethod
    def can_view_leave(company_id, user_id, leave):

        if leave.user_id == user_id:
            return True

        PermissionService.require_roles(
            company_id=company_id,
            user_id=user_id,
            allowed_roles=("manager", "owner")
        )

        return True

    @staticmethod
    def can_view_all_leaves(company_id, user_id):

        PermissionService.require_roles(
            company_id=company_id,
            user_id=user_id,
            allowed_roles=("manager", "owner")
        )

        return True

    @staticmethod
    def can_review(user_id, leave, membership):
        # Current rule:
        # only the assigned reviewer can review a leave request.
        
        # TODO:
        # Support additional review permissions such as
        # managers, owners, or delegated reviewers.
        return leave.assigned_reviewer_id == user_id

    @staticmethod
    def validate_reviewer_assignment(membership, reviewer_membership):
        role = membership.role
        reviewer_role = reviewer_membership.role
        if role == "employee":
            if reviewer_role not in ("manager", "owner"):
                raise PermissionDeniedError(message="Employee can only assign manager or owner")

        elif role == "manager":
            if reviewer_role != "owner":
                raise PermissionDeniedError(message="Manager can only assign owner")

        elif role == "owner":
            return

        else:
            raise PermissionDeniedError(message="Invalid role")
    