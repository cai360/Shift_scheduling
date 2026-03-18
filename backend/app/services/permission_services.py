from app.services.companyUser_service import CompanyUserService
from typing import Iterable

class PermissionService:
    @staticmethod
    def require_roles(*, company_id, user_id, allowed_roles:Iterable[str]):
        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=user_id
        )
        if not membership:
            raise PermissionError("Membership not found.")
        if membership.role not in allowed_roles:
            raise PermissionError("Permission denied.")
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
    