from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import selectinload
from app.config import BUSINESS_TZ, UTC_TZ
from app.extensions import db
from app.models.companies import Company
from app.models.shift import Shift
from app.models.shift_assignments import ShiftAssignment
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService
from app.errors.error_base import *

class ShiftService:

    @staticmethod
    def get_shift_detail(*, user_id, shift_id, company_id):
        membership = PermissionService.require_active_member(company_id=company_id, user_id=user_id)
        shift = (Shift.query.options(
                selectinload(Shift.assignments)
                .selectinload(ShiftAssignment.user)
            ).filter(
                Shift.id == shift_id,
                Shift.company_id == company_id,
                Shift.deleted_at.is_(None),
            ).first()
        )

        if not shift:
            raise NotFoundError(message="Shift not found.")

        is_manager = membership.role in ("manager", "owner")

        if not is_manager and shift.published_at is None:
            raise NotFoundError(message="Shift not found.")

        return shift


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
            local_start = datetime.combine(current_date, start_time)
            local_end = datetime.combine(current_date, end_time)

            if is_overnight:
                local_end += timedelta(days=1)
                if local_end.date() > end_date:
                    break

            local_slot_start = local_start
            while local_slot_start < local_end:
                local_slot_end = local_slot_start + timedelta(minutes=interval_minutes)
                slot_start_utc = ShiftService._local_to_utc(local_slot_start)
                slot_end_utc = ShiftService._local_to_utc(local_slot_end)
                if slot_start_utc <= now:
                    raise ValidationAppError("request includes past slots")
                candidate_slots.append((slot_start_utc, slot_end_utc))
                local_slot_start = local_slot_end

            current_date += timedelta(days=1)

        # reject duplicate slots inside the same request
        if len(candidate_slots) != len(set(candidate_slots)):
            raise ValidationAppError("Duplicate shift slots detected in request.")

        ShiftService._lock_company_for_shift_write(company_id)

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
    def list_shifts_by_company(*, company_id, user_id, status: str | None = None, from_: date | None = None,
    to_: date | None = None):

        CompanyService.get_company(company_id)

        membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

        if not membership:
            raise PermissionDeniedError(message="Access denied.")

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

        if from_ is not None:
            from_dt = datetime.combine(from_, time.min, tzinfo=BUSINESS_TZ)
            shifts = shifts.filter(Shift.end_at > from_dt)
        if to_ is not None:
            to_dt = datetime.combine(to_, time.min, tzinfo=BUSINESS_TZ)
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
        # locked here so nothing can change published_at between validation and the write below
        shifts = Shift.query.filter(
            Shift.id.in_(shift_ids)
        ).with_for_update().all()

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

        for shift in shifts:
            shift.published_at = now
        db.session.commit()

        return {
            "requested": len(shift_ids),
            "published": len(shifts),
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
        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id=user_id
        )

        ShiftService._lock_company_for_shift_write(company_id)

        shift = Shift.query.filter(
            Shift.id == shift_id,
            Shift.company_id == company_id,
            Shift.deleted_at.is_(None),
        ).with_for_update().first()
        if not shift:
            raise NotFoundError(message="Shift not found")

        if shift.published_at is not None:
            raise ConflictError(message="Cannot update a published shift.")

        new_start_naive = data.get("start_at")
        new_end_naive = data.get("end_at")

        new_start_at = (
            ShiftService._local_to_utc(new_start_naive)
            if new_start_naive is not None
            else shift.start_at
        )

        new_end_at = (
            ShiftService._local_to_utc(new_end_naive)
            if new_end_naive is not None
            else shift.end_at
        )

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

        if new_start_at != shift.start_at or new_end_at != shift.end_at:
            ShiftService._validate_shift_time_update(
                shift=shift,
                new_start_at=new_start_at,
                new_end_at=new_end_at,
            )

        new_capacity = data.get("capacity")
        if new_capacity is not None:
            ShiftService._validate_shift_capacity_update(
                shift=shift,
                new_capacity=new_capacity,
            )

        shift.start_at = new_start_at
        shift.end_at = new_end_at

        if new_capacity is not None:
            shift.capacity = new_capacity

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
    def _validate_shift_time_update(*, shift, new_start_at, new_end_at):
        assigned_user_ids = [
            row[0] for row in
            db.session.query(ShiftAssignment.user_id)
            .filter(
                ShiftAssignment.shift_id == shift.id,
                ShiftAssignment.deleted_at.is_(None),
            ).all()
        ]
        if not assigned_user_ids:
            return

        conflicting = (
            db.session.query(ShiftAssignment.user_id, ShiftAssignment.shift_id)
            .join(Shift, Shift.id == ShiftAssignment.shift_id)
            .filter(
                ShiftAssignment.user_id.in_(assigned_user_ids),
                ShiftAssignment.shift_id != shift.id,
                ShiftAssignment.deleted_at.is_(None),
                Shift.deleted_at.is_(None),
                Shift.end_at > new_start_at,
                Shift.start_at < new_end_at,
            )
            .all()
        )
        if conflicting:
            raise ConflictError(
                message="shift.time_update_employee_conflict",
                details={
                    "conflict_user_ids": sorted(set(row[0] for row in conflicting)),
                    "conflict_shift_ids": sorted(set(row[1] for row in conflicting)),
                },
            )

    @staticmethod
    def _validate_shift_capacity_update(*, shift, new_capacity):
        assignment_count = ShiftAssignment.query.filter(
            ShiftAssignment.shift_id == shift.id,
            ShiftAssignment.deleted_at.is_(None),
        ).count()
        if new_capacity < assignment_count:
            raise ConflictError(
                message="shift.capacity_too_low",
                details={
                    "current_assignment_count": assignment_count,
                    "requested_capacity": new_capacity,
                },
            )

    @staticmethod
    def _lock_company_for_shift_write(company_id):
        # global per-company lock serializes all shift writes for the company;
        # switch to a narrower (e.g. slot-range or advisory) lock if this becomes a throughput bottleneck.
        db.session.query(Company.id).filter(Company.id == company_id).with_for_update().first()

    @staticmethod
    def _local_to_utc(naive_dt):
        if naive_dt.tzinfo is not None:
            raise ValidationAppError("Datetime must be naive (no timezone). Provide local time.")
        return naive_dt.replace(tzinfo=BUSINESS_TZ).astimezone(UTC_TZ)

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
