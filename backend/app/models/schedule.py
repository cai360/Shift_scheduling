from app.extensions import db


class Schedule(db.Model):
    """
    Represents a schedule period (e.g., a weekly or monthly schedule)
    that groups multiple shifts within a company.
    """
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id', ondelete='CASCADE'),
        nullable=False
    )

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    published = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text('false')
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=db.func.now(),
        server_default=db.func.now(),
        nullable=False
    )

    company = db.relationship(
        'Company',
        back_populates='schedules'
    )

    shifts = db.relationship(
        'Shift',
        back_populates='schedule',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    def __repr__(self):
        """Readable string representation for debugging."""
        return (
            f"<Schedule id={self.id} company_id={self.company_id} "
            f"{self.start_date} → {self.end_date} published={self.published}>"
        )