from app.models.shift import Shift
from app.extensions import db
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.models.companies_users import CompanyUser
from datetime import datetime, timedelta
from app.config import BUSINESS_TZ, UTC_TZ

class ShiftService:

    @staticmethod
    def create_shifts_bulk(*, data, user_id, company_id):

        CompanyService.get_company(company_id)

        membership = CompanyUserService.get_active_membership(
            company_id=company_id,
            user_id=user_id
        )

        if not membership or membership.role != 'manager':
            raise PermissionError("Only manager allowed.")

        start_date = data["start_date"]
        end_date = data["end_date"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        interval_minutes = data["interval_minutes"]

        start_minutes = minutes_since_midnight(start_time)
        end_minutes = minutes_since_midnight(end_time)

        if end_time <= start_time:
            end_minutes += 24 * 60  # overnight

        duration_minutes = end_minutes - start_minutes

        if duration_minutes % interval_minutes != 0:
            raise ValueError(
                "Shift duration must be divisible by interval_minutes (wall-clock)"
            )
        
        with db.session.begin():
            current_date = start_date        

            while current_date <= end_date:
                local_start = datetime.combine(current_date, start_time, tzinfo=BUSINESS_TZ)
                local_end = datetime.combine(current_date, end_time, tzinfo=BUSINESS_TZ)

                if end_time <= start_time:
                    local_end += timedelta(days=1)

                start_at_utc = local_start.astimezone(UTC_TZ)
                end_at_utc = local_end.astimezone(UTC_TZ)
                
                slot_start = start_at_utc
                while slot_start < end_at_utc:
                    slot_end = slot_start + timedelta(minutes=interval_minutes)

                    db.session.add(
                        Shift(
                            company_id=company_id,
                            start_at=slot_start,
                            end_at=slot_end,
                            capacity=data["capacity"]
                        )
                    )

                    slot_start = slot_end
                
                current_date += timedelta(days=1)


def minutes_since_midnight(t):
    return t.hour * 60 + t.minute
