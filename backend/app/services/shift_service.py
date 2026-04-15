from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.orm import aliased, selectinload
from app.config import BUSINESS_TZ, UTC_TZ
from app.extensions import db
from app.models.shift import Shift
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService
from app.errors.error_base import *

class ShiftService:

    @staticmethod
    def create_shifts_bulk(*, data, user_id, company_id):
        """
        MVP behavior:
        - create draft shifts only
        - draft shifts may overlap
        - exact duplicate slots (same start_at, end_at) are rejected
        - overlap constraints are enforced at publish time
        - bulk creation is not idempotent
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
            raise  ValidationAppError("start date must be before or equal to end date")

        start_minutes = minutes_since_midnight(start_time)
        end_minutes = minutes_since_midnight(end_time)

        is_overnight = end_time <= start_time
        if is_overnight and start_date >= end_date:
            raise ValidationAppError(
                "Overnight shift generation requires end_date to be after start_date."
            )

        if is_overnight:
            end_minutes += 24 * 60

        duration_minutes = end_minutes - start_minutes

        if duration_minutes <= 0:
            raise ValidationAppError("invalid shift duration")

        if duration_minutes % interval_minutes != 0:
            raise ValidationAppError(
                "Shift duration must be divisible by interval_minutes (wall-clock)"
            )

        candidate_slots = []
        current_date = start_date
        now = datetime.now(tz=UTC_TZ)

        while current_date <= end_date:
            local_start = datetime.combine(
                current_date,
                start_time,
                tzinfo=BUSINESS_TZ
            )
            local_end = datetime.combine(
                current_date,
                end_time,
                tzinfo=BUSINESS_TZ
            )

            if is_overnight:
                local_end += timedelta(days=1)
                if local_end.date() > end_date:
                    break

            start_at_utc = local_start.astimezone(UTC_TZ)
            end_at_utc = local_end.astimezone(UTC_TZ)

            slot_start = start_at_utc
            while slot_start < end_at_utc:
                slot_end = slot_start + timedelta(minutes=interval_minutes)
                if slot_start <= now:
                    raise ValidationAppError("request includes past slots")
                
                candidate_slots.append((slot_start, slot_end))
                slot_start = slot_end

            current_date += timedelta(days=1)

        # reject duplicate slots inside the same request
        if len(candidate_slots) != len(set(candidate_slots)):
            raise ValidationAppError("Duplicate shift slots detected in request.")

        # reject exact duplicate active slots already in DB
        # TODO:  the range of DB duplicate querycan be narrower
        existing_shifts = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.deleted_at.is_(None),
            ).all()
        )

        existing_slot_set = {
            (shift.start_at, shift.end_at)
            for shift in existing_shifts
        }

        duplicate_slots = [
            (start_at, end_at)
            for start_at, end_at in candidate_slots
            if (start_at, end_at) in existing_slot_set
        ]

        if duplicate_slots:
            raise ConflictError("Exact duplicate shift slots already exist.")

        created_shifts = []
        for start_at, end_at in candidate_slots:
            shift = Shift(
                company_id=company_id,
                start_at=start_at,
                end_at=end_at,
                capacity=capacity,
            )
            db.session.add(shift)
            created_shifts.append(shift)

        db.session.commit()

        created_shifts.sort(key=lambda s: s.start_at)
        return created_shifts
    
    @staticmethod
    def list_shifts_by_company(*, company_id, user_id, status: str| None = None, from_: datetime | None = None,
    to_: datetime | None = None,): 

        CompanyService.get_company(company_id)

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionDeniedError(message="Access denied.")
        
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
            raise ValidationAppError("shift_ids must be unique")

        candidate_shifts = (
            Shift.query.filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.published_at.is_(None),
                Shift.deleted_at.is_(None),
            ).all()
        )

        if len(candidate_shifts) != len(shift_ids):
            raise ValidationAppError(message=
               "Some shift_ids are invalid for publishing."
            )

        overlap_candidate_ids = ShiftService._get_overlapping_candidate_shifts(
            candidate_shifts
        )
        if overlap_candidate_ids:
            raise ConflictError(message=
                f"Cannot publish shifts: candidate shifts overlap. shift_ids={overlap_candidate_ids}"
            )
        
        overlap_with_published_ids = (
            ShiftService._get_overlapping_published_shifts(
                company_id=company_id,
                shift_ids=shift_ids,
            )
        )

        if overlap_with_published_ids:
            raise ConflictError(message=
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
    def update_shift(*, company_id, shift_id, user_id, data):
        """
        MVP:
        - Only draft shifts can be updated
        - Time update recomputes start_at / end_at using BUSINESS_TZ
        - overlap is not validated here; it is enforced at publish time
        """
        shift = Shift.query.filter(
            Shift.id == shift_id,
            Shift.company_id == company_id,
            Shift.deleted_at.is_(None),
        ).first()
        if not shift:
            raise NotFoundError(message="Shift not found")

        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id=user_id
        )

        if shift.published_at is not None:
            raise ConflictError(message="Cannot update a published shift.")

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

            new_start_at = local_start.astimezone(UTC_TZ)
            new_end_at = local_end.astimezone(UTC_TZ)
            now = datetime.now(UTC_TZ)

            if new_start_at <= now:
                raise ValidationAppError("Cannot update shift to the past.")
            
            shift.start_at = new_start_at
            shift.end_at = new_end_at

        if "capacity" in data:
            shift.capacity = data["capacity"]

        db.session.commit()
        return shift


    @staticmethod
    def delete_shift(*, company_id, shift_id, user_id):
        """
        draft shift can be hard delete
        """
        shift = Shift.query.filter(
            Shift.id == shift_id,
            Shift.company_id == company_id,
            Shift.deleted_at.is_(None),
        ).first()
        if not shift:
            raise NotFoundError(message="Shift not found")
        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id = user_id
        )

        if shift.published_at is not None:
            raise ConflictError(message="Cannot delete a published shift.")
        
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
