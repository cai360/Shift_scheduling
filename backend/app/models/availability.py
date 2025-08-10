from app.extensions import db

class Availability(db.Model):
    __tablename__ = 'availabilities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False) 
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    user = db.relationship('User', back_populates='availabilities')

    __table_args__ = (
        db.Index('ix_user_availability_unique', 'date', 'user_id', 'start_time', 'end_time', unique=True),
    )