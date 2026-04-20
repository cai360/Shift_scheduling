from app.models import Unavailability
from app.models import ShiftAssignment
from app.models import Shift
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService
from app.services.datetimeRange_service import DateTimeRangeService
from app.extensions import db
from app.errors.error_base import *
from datetime import datetime
from app.config import UTC_TZ

class UnavailabilityService:
    @staticmethod
    def create_unavailability(data, user_id, company_id):
        try:
            membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
            if not membership:
                raise NotFoundError(message="User not found in this company")

            start_at = data["start_at"].astimezone(UTC_TZ)
            end_at = data["end_at"].astimezone(UTC_TZ)

            UnavailabilityService.validate_time_range(start_at, end_at)
            UnavailabilityService.validate_no_time_conflicts(user_id, company_id, start_at, end_at)
            
            unavailability = Unavailability(
                start_at=start_at,
                end_at=end_at,
                user_id=user_id, 
                company_id=company_id
            )
            db.session.add(unavailability)

            db.session.commit()
            return unavailability

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_unavailability(unavailability_id, user_id, company_id):
        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
        if not membership:
            raise NotFoundError(message="User not found in this company")
        
        unavailability = Unavailability.query.filter_by(
            id=unavailability_id,
            company_id=company_id,
            deleted_at=None
        ).first()

        if not unavailability:
            raise NotFoundError(message="Unavailability does not exists.")
        
        if unavailability.user_id == user_id:
            return unavailability

        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id=user_id
        )
        return unavailability
    

    def list_unavailabilities(user_id, company_id, scope="self"):

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionDeniedError(message="Insufficient permissions")

        query = (
            Unavailability.query.filter_by(company_id=company_id, deleted_at=None)
            .order_by(Unavailability.start_at)
        )

        if scope == "self":
            return query.filter_by(user_id= user_id).all()
        
        if scope == "all":
            if membership.role not in ("owner", "manager"):
                raise PermissionDeniedError(message="Insufficient permissions")
            return query.all()
        raise ValueError("Invalid scope.")
        
    @staticmethod
    def update_unavailability(unavailability_id, user_id, company_id, data):
        try: 
            unavailability = UnavailabilityService.get_unavailability(unavailability_id, user_id, company_id)

            if (unavailability.user_id != user_id):
                raise PermissionDeniedError(message="Insufficient permissions")

            start_at = data["start_at"].astimezone(UTC_TZ)
            end_at = data["end_at"].astimezone(UTC_TZ)


            UnavailabilityService.validate_time_range(start_at, end_at)
            UnavailabilityService.validate_no_time_conflicts(user_id, company_id, start_at, end_at,exclude_id=unavailability.id)
            
            unavailability.start_at = start_at
            unavailability.end_at = end_at

            db.session.commit()
            return unavailability
        except Exception:
            db.session.rollback()
            raise
    
    @staticmethod
    def delete_unavailability(unavailability_id, user_id, company_id):
        try:    
            unavailability = UnavailabilityService.get_unavailability(unavailability_id, user_id, company_id)
            
            if unavailability.user_id != user_id:
               PermissionDeniedError(message="Insufficient permissions")

            unavailability.deleted_at = datetime.now(tz=UTC_TZ)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
    
    @staticmethod
    def has_overlap_with_active_assignments(user_id, company_id, start_at, end_at):
        now = datetime.now(UTC_TZ)

        query = db.session.query(ShiftAssignment.id).join(
            Shift, ShiftAssignment.shift_id == Shift.id
        ).filter(
            ShiftAssignment.user_id == user_id,
            ShiftAssignment.deleted_at.is_(None),
            Shift.company_id == company_id,
            Shift.deleted_at.is_(None),
            Shift.published_at.is_not(None),
            Shift.end_at > now,
            Shift.start_at < end_at,
            Shift.end_at > start_at
        )
        return db.session.query(query.exists()).scalar()
    
    @staticmethod
    def validate_time_range(start_at, end_at):
        now = datetime.now(UTC_TZ)

        if start_at >= end_at:
            raise ValueError("start_at must be earlier than end_at.")

        if start_at <= now:
            raise ValueError("Unavailability must be in the future.")
        
    @staticmethod
    def validate_no_time_conflicts(user_id, company_id, start_at, end_at, exclude_id=None):
        if UnavailabilityService.has_overlap_with_active_assignments(
            user_id=user_id,
            company_id=company_id,
            start_at=start_at,
            end_at=end_at
        ):
            raise ValueError("Time range overlaps with future active assignments.")

        if DateTimeRangeService.has_overlap(
            Unavailability,
            user_id=user_id,
            company_id=company_id,
            start_at=start_at,
            end_at=end_at,
            exclude_id=exclude_id
        ):
            raise ValueError("Time range overlaps with existing unavailability.")

