from app.extensions import db

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    hash = db.Column(db.String)
    active = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime) 

    roles = db.relationship(
        "Role", 
        secondary=user_roles, 
        back_populates="users"
    )

    shift_assignments = db.relationship(
        'ShiftAssignment', 
        back_populates='user', 
        passive_deletes=True
    )
    availabilities = db.relationship(
        'Availability', 
        back_populates='user',
        passive_deletes=True
    )
    requested_swaps = db.relationship(
        'Swap', 
        foreign_keys='Swap.requester_id', 
        back_populates='requester'
    )

    responded_swaps = db.relationship(
        'Swap', 
        foreign_keys='Swap.responder_id',   
        back_populates='responder'
    )




