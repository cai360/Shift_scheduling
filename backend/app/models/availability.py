from app.extensions import db

class Availability(db.Model):
    """
    Represents an employee's available working time for a specific date.
    Each availability record belongs to both a company and a user.
    """
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)


    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # The specific date of the availability
    date = db.Column(db.Date, nullable=False)

    # Start and end times of the available period
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)

    user = db.relationship('User', back_populates='availabilities')
    company = db.relationship('Company', back_populates='availabilities')

    # ensures a user cannot have overlapping identical records
    __table_args__ = (
        db.Index(
            'ix_company_user_availability_unique',
            'company_id',
            'user_id',
            'date',
            'starting_time',
            'ending_time',
            unique=True
        ),
    )
