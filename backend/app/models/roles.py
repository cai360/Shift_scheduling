from app.extensions import db
from app.constants.role import RoleType 


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.role_type}>"