import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
from sqlalchemy.sql import func #取得 SQL function 物件



class BaseModel(db.Model):
    __abstract__ = True   # 不會創 table，只是用來被繼承

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )