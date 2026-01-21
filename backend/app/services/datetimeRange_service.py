from app.extensions import db

class DateTimeRangeService:
    @staticmethod
    def validate_time_range(start_at, end_at):
        if end_at <= start_at:
            raise ValueError("end_at must be after start_at.")

    @staticmethod
    def has_overlap(Model, user_id, company_id, start_at, end_at, exclude_id=None):
        query = Model.query.filter(
            Model.user_id == user_id,
            Model.company_id == company_id,
            Model.deleted_at.is_(None),
            Model.start_at < end_at,
            Model.end_at > start_at
        ) 

        if exclude_id:
            query = query.filter(Model.id != exclude_id)

        return db.session.query(query.exists()).scalar()
