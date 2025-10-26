from app.extensions import db

class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    starting_time = db.Column(db.Time, nullable=False)
    ending_time = db.Column(db.Time, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=db.func.now(), server_default=db.func.now(), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='availabilities', lazy='selectin')
    company = db.relationship('Company', back_populates='availabilities', lazy='selectin')

    __table_args__ = (
        db.UniqueConstraint(
            'company_id', 'user_id', 'date', 'starting_time', 'ending_time',
            name='uq_company_user_availability'
        ),
    )

    def __repr__(self):
        return f"<Availability id={self.id} user_id={self.user_id} date={self.date}>"