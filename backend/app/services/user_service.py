from app.models.user import User
from app.extensions import db
from app.models.companies_users import CompanyUser
from app.services.auth_service import AuthService
from app.errors.error_base import *
from datetime import datetime, timezone
from app.models.companies import Company

class UserService:

    @staticmethod
    def get_user(user_id):
        user = User.query.filter_by(
            id=user_id, 
            deleted_at=None
        ).first()

        if not user:
            raise NotFoundError(message="User not found")
        return user
    
    @staticmethod
    def update_user(user_id, data):
        user = UserService.get_user(user_id)

        if "email" in data:
            existing = User.query.filter_by(email=data["email"]).first()
            if existing and existing.id != user_id:
                raise ConflictError("Email already exists")
        
        for key, value in data.items():
            setattr(user, key, value)
        user.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return user


    @staticmethod
    def update_user_password(user_id, old_password, new_password):
        user = UserService.get_user(user_id)
        
        if not AuthService.verify_password(old_password, user.hash):
            raise ValidationAppError("Old password is incorrect")
        
        hash_password = AuthService.hash_password(new_password)
        user.hash = hash_password
        user.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return {"message": "Password updated"}

    
    @staticmethod
    def soft_delete_user(user_id):
        user = UserService.get_user(user_id)
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        user.updated_at = now
        #release the email
        user.email = f"{user.email}.deleted.{user.id}"

        memberships = CompanyUser.query.filter_by(
            user_id = user_id,
            deleted_at = None
        ).all()

        for c_u in memberships:
            c_u.deleted_at = now

        db.session.commit()
        return {"message": "User's account deleted!"}
    
    @staticmethod
    def list_companies_for_user(user_id):
        companies = (
            db.session.query(Company)
            .join(CompanyUser, CompanyUser.company_id == Company.id)
            .filter(
                CompanyUser.user_id == user_id,
                Company.deleted_at.is_(None),
                CompanyUser.deleted_at.is_(None)
            )
            .all()
        )
        return companies

    #check user role (TODO in the future)
    @staticmethod
    def check_permission(user_id, action):
        ...

    
        

  
    

    




    
