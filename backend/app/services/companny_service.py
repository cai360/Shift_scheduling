from app.models.user import User
from app.models.companies import Company
from app.extensions import db
from app.models.companies_users import CompanyUser
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
                role="manager"
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
    def list_companies_for_user(user_id):
        companies = (
            db.session.query(Company)
            .join(CompanyUser, CompanyUser.company_id == Company.id)
            .filter(
                CompanyUser.user_id == user_id,
                CompanyUser.deleted_at.is_(None), 
                Company.deleted_at.is_(None)
            )
            .all()
        )
        return companies


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
        company = CompanyService.get_company(company_id)

        company_user = CompanyUser.query.filter_by(
            company_id=company_id,
            user_id=user_id
        ).first()

        if not company_user or company_user.role != "manager":
            raise PermissionError("Only manager can delete this company.")

        company.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
        return True


    @staticmethod
    def join_company(company_id, user_id):
        """MVP: Only creator is manager. Everyone else is member."""
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