from app.extensions import db
from .base import BaseModel
from datetime import datetime

class Company(BaseModel):
    __tablename__ = 'companies'

    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.boolean, nullable= False, default=True)
    deleted_at = db.Column(db.Datetime(timezone=True), nullable=True)
    

   