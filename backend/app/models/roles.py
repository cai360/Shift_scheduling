from app.extensions import db
from app.constants.role import RoleType 


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.Integer, unique=True, nullable=False)

    users = db.relationship(
        "User", 
        secondary="user_roles", 
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.role_type}>"