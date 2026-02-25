from app.models.shift import Shift
from app.extensions import db
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService
from app.models.companies_users import CompanyUser
from datetime import datetime, timedelta
from app.config import BUSINESS_TZ, UTC_TZ
from sqlalchemy import exists, and_
from sqlalchemy.orm import selectinload

class ShiftService:

    @staticmethod
    def create_shifts_bulk(*, data, user_id, company_id):
        """
        NOTE (MVP scope, to be addressed later):

        1. Overlap / Duplicate Protection - This method does not prevent generating shifts that overlap with existing ones.
        2. Idempotency- Repeating the same bulk request may generate duplicate shifts.
        3. Publish State Enforcement - This method does not check whether shifts are already published.
        4. Bulk Insert Optimization - Shifts are inserted one by one via ORM.
        """
        CompanyService.get_company(company_id)

        PermissionService.require_can_manage_company(
            company_id=company_id, 
            user_id=user_id
        )

        start_date = data["start_date"]
        end_date = data["end_date"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        interval_minutes = data["interval_minutes"]
        capacity = data["capacity"]

        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")
        
        if end_date == start_date and start_time >= end_time:
            raise ValueError("endtime must be before start time")

        start_minutes = minutes_since_midnight(start_time)
        end_minutes = minutes_since_midnight(end_time)

        if end_time <= start_time:
            end_minutes += 24 * 60  # overnight

        duration_minutes = end_minutes - start_minutes

        if duration_minutes % interval_minutes != 0:
            raise ValueError(
                "Shift duration must be divisible by interval_minutes (wall-clock)"
            )

        created_shifts = []

        current_date = start_date
        while current_date <= end_date:
            local_start = datetime.combine(
                current_date, start_time, tzinfo=BUSINESS_TZ
            )
            local_end = datetime.combine(
                current_date, end_time, tzinfo=BUSINESS_TZ
            )

            if end_time <= start_time:
                local_end += timedelta(days=1)

            start_at_utc = local_start.astimezone(UTC_TZ)
            end_at_utc = local_end.astimezone(UTC_TZ)

            slot_start = start_at_utc
            while slot_start < end_at_utc:
                slot_end = slot_start + timedelta(minutes=interval_minutes)

                shift = Shift(
                    company_id=company_id,
                    start_at=slot_start,
                    end_at=slot_end,
                    capacity=capacity,
                )

                db.session.add(shift)
                created_shifts.append(shift)

                slot_start = slot_end

            current_date += timedelta(days=1)

        db.session.commit()
        return created_shifts
    
    @staticmethod
    def list_shifts_by_company(*, company_id, user_id, status: str| None = None, from_: datetime | None = None,
    to_: datetime | None = None,): 

        CompanyService.get_company(company_id)

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionError("Not a company member.")
        
        shifts = (
            Shift.query.options(selectinload(Shift.assignments))
                .filter(Shift.company_id == company_id,
                        Shift.deleted_at.is_(None))
        )

        if membership.role != 'manager':
            shifts = shifts.filter(Shift.published_at.isnot(None))

        if status == 'published':
            shifts = shifts.filter(Shift.published_at.isnot(None))
        
        if from_:
            shifts = shifts.filter(
                Shift.end_at > from_
            )
        if to_:
            shifts = shifts.filter(
                Shift.start_at < to_
            )
        shifts = shifts.order_by(Shift.start_at.asc()).all()

        return shifts


    @staticmethod
    def publish_shifts(*, company_id, user_id, shift_ids):
        CompanyService.get_company(company_id)

        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id=user_id
        )

        candidate_shifts = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.published_at.is_(None),
                Shift.deleted_at.is_(None),
            ).all()
        )

        candidate_ids = [s.id for s in candidate_shifts]

        if not candidate_ids:
            return {"requested": len(shift_ids), "eligible": 0, "published": 0}

        # TODO: return overlapping shift ids for better UX
        if ShiftService._has_overlap_with_published(
            company_id=company_id,
            shift_ids=candidate_ids
        ):
            raise ValueError("Cannot publish shifts: overlap with existing published shifts.")

        now = datetime.now(tz=UTC_TZ)

        updated_count = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.id.in_(candidate_ids),
                Shift.published_at.is_(None),
                Shift.deleted_at.is_(None),
            )
            .update(
                {Shift.published_at: now},
                synchronize_session=False
            )
        )
        db.session.commit()

        return {"requested": len(shift_ids), "eligible": len(candidate_ids), "published": updated_count}
        
    @staticmethod
    def _has_overlap_with_published(*, company_id, shift_ids):
        """
        Return True if any candidate shift (id) overlaps with any publised shifts in the same company.
        """
        existing = db.aliased(Shift)
        candidate = db.aliased(Shift)

        overlap_exists_query = (
            db.session.query(
                exists().where(
                    and_(
                        existing.company_id == company_id,
                        existing.deleted_at.is_(None),
                        existing.published_at.isnot(None),

                        candidate.company_id == company_id,
                        candidate.deleted_at.is_(None),
                        candidate.published_at.is_(None),
                        candidate.id.in_(shift_ids),

                        existing.start_at < candidate.end_at,
                        existing.end_at > candidate.start_at
                    )                 
                )
            )
        )

        return overlap_exists_query.scalar()
    
    @staticmethod
    def update_shift(*, shift_id, user_id, data):
        """
        MVP:
        - Only draft shifts can be updated
        - Time update recomputes start_at / end_at using BUSINESS_TZ
        """
        shift = Shift.query.get_or_404(shift_id)

        PermissionService.require_can_manage_company(
            company_id=shift.company_id,
            user_id=user_id
        )

        if shift.published_at is not None:
            raise ValueError("Cannot update a published shift.")

        if "start_time" in data or "end_time" in data:
            local_date = shift.start_at.astimezone(BUSINESS_TZ).date()

            start_time = data.get(
                "start_time",
                shift.start_at.astimezone(BUSINESS_TZ).time()
            )
            end_time = data.get(
                "end_time",
                shift.end_at.astimezone(BUSINESS_TZ).time()
            )

            local_start = datetime.combine(
                local_date, start_time, tzinfo=BUSINESS_TZ
            )
            local_end = datetime.combine(
                local_date, end_time, tzinfo=BUSINESS_TZ
            )

            if end_time <= start_time:
                local_end += timedelta(days=1)

            shift.start_at = local_start.astimezone(UTC_TZ)
            shift.end_at = local_end.astimezone(UTC_TZ)

        if "capacity" in data:
            shift.capacity = data["capacity"]

        db.session.commit()
        return shift


    @staticmethod
    def delete_shift(*, shift_id, user_id):
        """
        draft shift can be hard delete
        """
        shift = Shift.query.get_or_404(shift_id)
        PermissionService.require_can_manage_company(
            company_id=shift.company_id,
            user_id = user_id
        )

        if shift.published_at is not None:
            raise ValueError("Cannot delete a published shift.")
        
        db.session.delete(shift)
        db.session.commit()



def minutes_since_midnight(t):
    return t.hour * 60 + t.minute
