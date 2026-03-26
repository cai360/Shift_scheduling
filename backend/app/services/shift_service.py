from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import aliased, selectinload
from app.config import BUSINESS_TZ, UTC_TZ
from app.extensions import db
from app.models.shift import Shift
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService

class ShiftService:

    @staticmethod
    def create_shifts_bulk(*, data, user_id, company_id):
        """
        MVP behavior:
        - create draft shifts only
        - draft shifts may overlap
        - overlap invariant is enforced at publish time
        - repeated bulk requests are not idempotent
        - shifts are inserted via ORM one by one
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
            raise ValueError("start date must be before or equal to end date")

        start_minutes = minutes_since_midnight(start_time)
        end_minutes = minutes_since_midnight(end_time)

        is_overnight = end_time <= start_time
        if is_overnight and start_date >= end_date:
            raise ValueError(
                "Overnight shift generation requires end_date to be after start_date."
            )
        if is_overnight:
            end_minutes += 24 * 60  # overnight

        duration_minutes = end_minutes - start_minutes

        if duration_minutes <= 0:
            raise ValueError("invalid shift duration")

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
                if local_end.date() > end_date:
                    break


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
        return created_shifts.sort(key=lambda s: s.start_at)
    
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

        is_manager = membership.role in ("owner", "manager")

        if not is_manager:
            shifts = shifts.filter(Shift.published_at.isnot(None))
        else:
            if status == "published":
                shifts = shifts.filter(Shift.published_at.isnot(None))
            elif status == "draft":
                shifts = shifts.filter(Shift.published_at.is_(None))
        
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

        if len(shift_ids) != len(set(shift_ids)):
            raise ValueError("shift_ids must be unique")

        candidate_shifts = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.published_at.is_(None),
                Shift.deleted_at.is_(None),
            ).all()
        )

        if len(candidate_shifts) != len(shift_ids):
            raise ValueError(
                "Some shifts are invalid, deleted, already published, or not in this company."
            )

        overlap_candidate_ids = ShiftService._get_overlapping_candidate_shifts(
            candidate_shifts
        )
        if overlap_candidate_ids:
            raise ValueError(
                f"Cannot publish shifts: candidate shifts overlap. shift_ids={overlap_candidate_ids}"
            )
        
        overlap_with_published_ids = (
            ShiftService._get_overlapping_published_shifts(
                company_id=company_id,
                shift_ids=shift_ids,
            )
        )

        if overlap_with_published_ids:
            raise ValueError(
                f"Cannot publish shifts: overlap with existing published shifts. shift_ids={overlap_with_published_ids}"
            )

        now = datetime.now(tz=UTC_TZ)

        updated_count = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.published_at.is_(None),
                Shift.deleted_at.is_(None),
            )
            .update(
                {Shift.published_at: now},
                synchronize_session=False
            )
        )
        db.session.commit()

        return {
            "requested": len(shift_ids),
            "eligible": len(shift_ids),
            "published": updated_count,
        }
        
    @staticmethod
    def _get_overlapping_published_shifts(*, company_id, shift_ids):
        """
        Return candidate draft shift ids that overlap with existing published shifts
        in the same company.
        """
        existing = aliased(Shift) #self join
        candidate = aliased(Shift)

        rows = (
            db.session.query(candidate.id)
            .join(
                existing,
                and_(
                    existing.company_id == company_id,
                    existing.deleted_at.is_(None),
                    existing.published_at.isnot(None),
                    existing.start_at < candidate.end_at,
                    existing.end_at > candidate.start_at,
                ),
            )
            .filter(
                candidate.company_id == company_id,
                candidate.deleted_at.is_(None),
                candidate.published_at.is_(None),
                candidate.id.in_(shift_ids),
            )
            .distinct()
            .all()
        )

        return [row[0] for row in rows]
    
    @staticmethod
    def update_shift(*, shift_id, user_id, data):
        """
        MVP:
        - Only draft shifts can be updated
        - Time update recomputes start_at / end_at using BUSINESS_TZ
        - overlap is not validated here; it is enforced at publish time
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

    @staticmethod
    def _get_overlapping_candidate_shifts(candidate_shifts):
        sorted_shifts = sorted(candidate_shifts, key=lambda s: s.start_at)
        overlap_ids = set()

        for i in range(len(sorted_shifts) - 1):
            current_shift = sorted_shifts[i]
            next_shift = sorted_shifts[i + 1]

            if current_shift.end_at > next_shift.start_at:
                overlap_ids.add(current_shift.id)
                overlap_ids.add(next_shift.id)

        return list(overlap_ids)



def minutes_since_midnight(t):
    return t.hour * 60 + t.minute
