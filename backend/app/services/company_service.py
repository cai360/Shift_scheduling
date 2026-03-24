from app.models.companies import Company
from app.extensions import db
from app.models.companies_users import CompanyUser
from app.models.shift import Shift
from app.models.shift_assignments import ShiftAssignment
from app.models.shift_takeovers import ShiftTakeover
from app.models.leaves import Leave
from app.models.unavailability import Unavailability
from datetime import datetime, timezone

class CompanyService:

    @staticmethod
    def create_company(data, user_id):
        try:
            company = Company(**data)
            db.session.add(company)
            db.session.flush()

            company_user = CompanyUser(
                company_id=company.id,
                user_id=user_id,
                role="owner"
            )
            db.session.add(company_user)

            db.session.commit()
            return company

        except Exception:
            db.session.rollback()
            raise


    @staticmethod
    def get_company(company_id, user_id=None):
        company = Company.query.filter(
            Company.id == company_id,
            Company.deleted_at.is_(None)
        ).first()

        if not company:
            raise ValueError("Company not found")

        return company


    @staticmethod
    def update_company(company_id, data, user_id):
        company = CompanyService.get_company(company_id)

        company_user = CompanyUser.query.filter_by(
            company_id=company_id,
            user_id=user_id
        ).first()

        if not company_user or company_user.role != "manager":
            raise PermissionError("Only manager can update company information.")

        for key, value in data.items():
            setattr(company, key, value)

        db.session.commit()
        return company


    @staticmethod
    def soft_delete_company(company_id, user_id):
        """
        In the MVP stage, company deletion is treated as tenant deactivation.

        All related business data are soft deleted.
        Unavailability records are hard deleted.
        """
        company = CompanyService.get_company(company_id)
        now = datetime.now(timezone.utc)

        try:
            company.deleted_at = now
            CompanyUser.query.filter(
                CompanyUser.company_id == company_id,
                CompanyUser.deleted_at.is_(None)
            ).update(
                {"deleted_at": now},
                synchronize_session=False
            )

            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.deleted_at.is_(None)
            ).update(
                {"deleted_at": now},
                synchronize_session=False
            )

            ShiftAssignment.query.filter(
                ShiftAssignment.shift_id.in_(
                    db.session.query(Shift.id).filter(
                        Shift.company_id == company_id
                    )
                ),
                ShiftAssignment.deleted_at.is_(None)
            ).update(
                {"deleted_at": now},
                synchronize_session=False
            )

            ShiftTakeover.query.filter(
                ShiftTakeover.assignment_id.in_(
                    db.session.query(ShiftAssignment.id).filter(
                        ShiftAssignment.shift_id.in_(
                            db.session.query(Shift.id).filter(
                                Shift.company_id == company_id
                            )
                        )
                    )
                ),
                ShiftTakeover.deleted_at.is_(None)
            ).update(
                {"deleted_at": now},
                synchronize_session=False
            )

            Leave.query.filter(
                Leave.company_id == company_id,
                Leave.deleted_at.is_(None)
            ).update(
                {"deleted_at": now},
                synchronize_session=False
            )

            Unavailability.query.filter(
                Unavailability.company_id == company_id
            ).delete(
                synchronize_session=False
            )

            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise

  
        

