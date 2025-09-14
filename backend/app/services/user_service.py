
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app import models
from app.services.auth_service import AuthService

class UserService:
    @staticmethod
    def _pwd_field() -> str:
        if hasattr(models.User, "hash") : return "hash"
        if hasattr(models.User, "password_hash") : return "password_hash"
        

    @staticmethod
    def find_user_by_email(email: str | None):
        U = models.User
        if not hasattr(U, "email"):
            return None
        return U.query.filter(U.email == email).first()
        

    @staticmethod
    def create_user(data: dict) -> models.User:
        if "password" in data and data["password"]:
            field = UserService._pwd_field()
            data[field] = AuthService.hash_password(data.pop("password"))
        user = models.User(**data)
        db.session.add(user)
        try: db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("oh no something is wrong", e)
        return user
    

    @staticmethod
    def update_user(id: int, data: dict) -> models.User:
        user = db.session.get(models.User, id)
        if not user:
            raise ValueError("User not found")
        if "password" in data and data["password"]:
            field = UserService._pwd_field()
            setattr(user, field, AuthService.hash_password(data.pop("password")))   

        for key, value in data.items():
            setattr(user, key, value)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise ValueError("oh no something is wrong")
        return user
    

    
    @staticmethod
    def delete_user(id:int) -> models.User:
        user = db.session.get(models.User, id)
        if not user:
            raise ValueError("User not found")
        user.active = False
        db.session.commit()
        return user
    




    
