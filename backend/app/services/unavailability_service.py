from app.models import User, Company, CompanyUser, Unavailability
from app.extensions import db
from datetime import datetime, timezone
from werkzeug.exceptions import Forbidden, NotFound
from uuid import UUID

class UnavailabilityService:
    @staticmethod
    def create_unavailability(data, user_id, company_id):
        try:
            if not CompanyUser.query.filter_by(
                user_id=user_id,
                company_id=company_id
            ).first():
                raise Forbidden("User not in this company")

            if data["end_at"] <= data["start_at"]:
                raise ValueError("end_at must be after start_at")
            
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
            company_id=company_id
        ).first()

        if not unavailability:
            raise NotFound("Unavailability not found")

        if not CompanyUser.query.filter_by(
            user_id=user_id,
            company_id=company_id
        ).first():
            raise Forbidden("Not allowed")
        
        return unavailability

    def list_unavailabilities(user_id, company_id):
        company_user = CompanyUser.query.filter_by(
            company_id=company_id,
            user_id=user_id
        ).first()

        if not company_user:
            raise Forbidden("User is not in this company")

        if company_user.role == "manager":
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

        print(unavailability.id)
        print(unavailability.user_id)
        print(user_id)
        print(unavailability.user_id == UUID(user_id))
        print(unavailability.company_id)
        if data["end_at"] <= data["start_at"]:
            raise ValueError("end_at must be after start_at")
            
        if not unavailability:
            raise NotFound("Unavailability not found")

        company_user = (
            CompanyUser.query
            .filter_by(
                user_id=user_id,
                company_id=company_id
            )
            .first()
        )

        if not company_user:
            raise Forbidden("User not in this company")

        if (unavailability.user_id != UUID(user_id)):
            raise Forbidden("Insufficient permissions")

        for key, value in data.items():
            setattr(unavailability, key, value)

        db.session.commit()
        return unavailability
    
    @staticmethod
    def delete_unavailability(unavailability_id, user_id, company_id):
        print("company_id:", company_id)
        print("unavailability_id:", unavailability_id) 
        unavailability = UnavailabilityService.get_unavailability(unavailability_id, user_id, company_id)

        company_user = (
            CompanyUser.query
            .filter_by(
                user_id=user_id,
                company_id=company_id
            )
            .first()
        )
        if not company_user:
            raise Forbidden("User not in this company")

        if (unavailability.user_id != UUID(user_id)):
            raise Forbidden("Insufficient permissions")

        unavailability.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return True