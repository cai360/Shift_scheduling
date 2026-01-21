from app.models import Unavailability
from app.services.companyUser_service import CompanyUserService
from app.services.datetimeRange_service import DateTimeRangeService
from app.extensions import db
from datetime import datetime, timezone
from werkzeug.exceptions import Forbidden, NotFound
from uuid import UUID

class UnavailabilityService:
    @staticmethod
    def create_unavailability(data, user_id, company_id):
        try:
            membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
            if not membership:
                raise Forbidden("User not in this company")

            UnavailabilityService.validate_time_range(data)

            if DateTimeRangeService.has_overlap(
                Unavailability,
                user_id=user_id,
                company_id=company_id,
                start_at=data["start_at"],
                end_at=data["end_at"]
            ):
                raise ValueError("Time range overlaps with existing unavailability.")
            
            unavailability = Unavailability(
                **data, 
                user_id=user_id, 
                company_id=company_id
            )
            db.session.add(unavailability)

            db.session.commit()
            return unavailability

        except Exception:
            db.session.rollback()
            raise

    def get_unavailability(unavailability_id, user_id, company_id):
        unavailability = Unavailability.query.filter_by(
            id=unavailability_id,
            company_id=company_id,
            deleted_at=None
        ).first()

        if not unavailability:
            raise NotFound("Unavailability does not exists.")

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
        if not membership:
            raise Forbidden("Not a company member.")
        
        return unavailability

    def list_unavailabilities(user_id, company_id):

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionError("Not a company member.")

        if membership.role == "manager":
            return (
                Unavailability.query
                .filter_by(company_id=company_id)
                .order_by(Unavailability.start_at)
                .all()
            )

        return (
            Unavailability.query
            .filter_by(company_id=company_id, user_id=user_id)
            .order_by(Unavailability.start_at)
            .all()
        )

    def update_unavailability(unavailability_id, user_id, company_id, data):
        unavailability = UnavailabilityService.get_unavailability(unavailability_id, user_id, company_id)

        if (unavailability.user_id != UUID(user_id)):
            raise Forbidden("Insufficient permissions")

        UnavailabilityService.validate_time_range(data)

        if DateTimeRangeService.has_overlap(
            Unavailability,
            user_id=user_id,
            company_id=company_id,
            start_at=data["start_at"],
            end_at=data["end_at"],
            exclude_id=unavailability.id
        ):
            raise ValueError("Time range overlaps with existing unavailability.")
        
        for key, value in data.items():
            setattr(unavailability, key, value)

        db.session.commit()
        return unavailability
    
    @staticmethod
    def delete_unavailability(unavailability_id, user_id, company_id):
        unavailability = UnavailabilityService.get_unavailability(unavailability_id, user_id, company_id)
        
        if (unavailability.user_id != UUID(user_id)):
            raise Forbidden("Insufficient permissions")

        unavailability.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return True