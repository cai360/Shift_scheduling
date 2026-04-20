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
    