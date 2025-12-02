from app.extensions import db
from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(64), nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(64),  unique=True, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

   