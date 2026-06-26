from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import selectinload
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
        - exact duplicate slots are rejected
        - employee assignment overlap is enforced when assigning shifts
        - publishing does not require shifts to be assigned
        - published shifts can still be assigned
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

        ShiftService._validate_no_duplicate_slots(
            company_id=company_id,
            slots=candidate_slots,
        )

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
    def list_shifts_by_company(*, company_id, user_id, status: str| None = None, from_: date | None = None,
    to_: date | None = None,): 

        CompanyService.get_company(company_id)

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionDeniedError(message="Access denied.")
        
        from_dt = (
            datetime.combine(from_, time.min, tzinfo=BUSINESS_TZ)
            if from_
            else None
        )

        to_dt = (
            datetime.combine(to_, time.min, tzinfo=BUSINESS_TZ)
            if to_
            else None
        )

        shifts = (
            Shift.query.options(selectinload(Shift.assignments))
            .filter(
                Shift.company_id == company_id,
                Shift.deleted_at.is_(None),
            )
        )

        is_manager = membership.role in ("owner", "manager")

        if not is_manager:
            shifts = shifts.filter(Shift.published_at.isnot(None))
        else:
            if status == "published":
                shifts = shifts.filter(Shift.published_at.isnot(None))
            elif status == "draft":
                shifts = shifts.filter(Shift.published_at.is_(None))
        
        if from_dt:
            shifts = shifts.filter(Shift.end_at > from_dt)
        if to_dt:
            shifts = shifts.filter(Shift.start_at < to_dt)
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

        # ---- validation: invalid / already published ----
        shifts = Shift.query.filter(
            Shift.id.in_(shift_ids)
        ).all()

        found_by_id = {shift.id: shift for shift in shifts}

        not_found_ids = [
            shift_id for shift_id in shift_ids
            if shift_id not in found_by_id
        ]

        invalid_shift_ids = []
        already_published_ids = []

        for shift in shifts:
            if shift.company_id != company_id or shift.deleted_at is not None:
                invalid_shift_ids.append(shift.id)
            elif shift.published_at is not None:
                already_published_ids.append(shift.id)

        invalid_shift_ids = sorted(set(not_found_ids + invalid_shift_ids))
        already_published_ids = sorted(already_published_ids)

        if invalid_shift_ids:
            raise ValidationAppError(
                f"Some shift_ids are invalid for publishing. shift_ids={invalid_shift_ids}"
            )

        if already_published_ids:
            raise ConflictError(
                f"Some shifts are already published. shift_ids={already_published_ids}"
            )

        # ---- publish ----
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
    def update_shift(*, company_id, shift_id, user_id, data):
        """
        MVP:
        - Only draft shifts can be updated
        - start_at / end_at are updated directly from submitted datetimes
        - shift time overlap is allowed; employees cannot be assigned to overlapping shifts
        - exact duplicate slots (same start_at + end_at) are rejected within the same company
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

        new_start_at = data.get("start_time", shift.start_at)
        new_end_at = data.get("end_time", shift.end_at)

        new_start_at = new_start_at.astimezone(UTC_TZ)
        new_end_at = new_end_at.astimezone(UTC_TZ)

        if new_start_at >= new_end_at:
            raise ValidationAppError("end_time must be later than start_time.")

        now = datetime.now(tz=UTC_TZ)
        if new_start_at <= now:
            raise ValidationAppError("Cannot update shift to the past.")

        ShiftService._validate_no_duplicate_slots(
            company_id=company_id,
            slots=[(new_start_at, new_end_at)],
            exclude_shift_id=shift_id,
        )

        shift.start_at = new_start_at
        shift.end_at = new_end_at

        if "capacity" in data:
            shift.capacity = data["capacity"]

        db.session.commit()
        return shift


    @staticmethod
    def delete_shift(*, company_id, shift_id, user_id):
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
            # TODO: support soft delete for published shifts
            raise ConflictError(message="Cannot delete a published shift.")
        db.session.delete(shift)
        db.session.commit()

    @staticmethod
    def _validate_no_duplicate_slots(*, company_id, slots, exclude_shift_id=None):
        if not slots:
            return

        min_start = min(start for start, _ in slots)
        max_end = max(end for _, end in slots)

        query = Shift.query.filter(
            Shift.company_id == company_id,
            Shift.deleted_at.is_(None),
            Shift.start_at < max_end,
            Shift.end_at > min_start,
        )
        if exclude_shift_id is not None:
            query = query.filter(Shift.id != exclude_shift_id)

        existing_slot_set = {(s.start_at, s.end_at) for s in query.all()}

        if any((start, end) in existing_slot_set for start, end in slots):
            raise ConflictError("Exact duplicate shift slots already exist.")


    # @staticmethod
    # def _get_overlapping_candidate_shifts(candidate_shifts):
    #     sorted_shifts = sorted(candidate_shifts, key=lambda s: s.start_at)
    #     overlap_ids = set()
    #     for i in range(len(sorted_shifts) - 1):
    #         current_shift = sorted_shifts[i]
    #         next_shift = sorted_shifts[i + 1]
    #         if current_shift.end_at > next_shift.start_at:
    #             overlap_ids.add(current_shift.id)
    #             overlap_ids.add(next_shift.id)
    #     return sorted(overlap_ids)

    # @staticmethod
    # def _get_overlapping_published_shifts(*, company_id, shift_ids):
    #     from sqlalchemy import and_
    #     from sqlalchemy.orm import aliased
    #     existing = aliased(Shift)
    #     candidate = aliased(Shift)
    #     rows = (
    #         db.session.query(candidate.id)
    #         .join(
    #             existing,
    #             and_(
    #                 existing.company_id == company_id,
    #                 existing.deleted_at.is_(None),
    #                 existing.published_at.isnot(None),
    #                 existing.start_at < candidate.end_at,
    #                 existing.end_at > candidate.start_at,
    #             ),
    #         )
    #         .filter(
    #             candidate.company_id == company_id,
    #             candidate.deleted_at.is_(None),
    #             candidate.published_at.is_(None),
    #             candidate.id.in_(shift_ids),
    #         )
    #         .distinct()
    #         .all()
    #     )
    #     return sorted([row[0] for row in rows])


def minutes_since_midnight(t):
    return t.hour * 60 + t.minute
