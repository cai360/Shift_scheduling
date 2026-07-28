from app.extensions import db
from app.models import ShiftAssignment, Shift, Unavailability
from app.models.companies_users import CompanyUser
from app.services.company_service import CompanyService
from app.services.permission_services import PermissionService

from datetime import datetime
from app.config import UTC_TZ
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.errors.error_base import *

class AssignmentService:
    @staticmethod
    def assign_user_to_shifts(*, company_id, actor_user_id, target_user_id, shift_ids):
        CompanyService.get_company(company_id=company_id)

        PermissionService.require_can_manage_company(company_id=company_id, user_id=actor_user_id)

        membership = (
            CompanyUser.query
            .filter(
                CompanyUser.company_id == company_id,
                CompanyUser.user_id == target_user_id,
                CompanyUser.deleted_at.is_(None),
            )
            .with_for_update()
            .first()
        )
        if not membership:
            raise NotFoundError(message="Company member not found")
        
        if len(shift_ids) != len(set(shift_ids)):
            raise ValidationAppError("shift_ids must be unique")

        shifts = (
            Shift.query
            .filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.deleted_at.is_(None),
            ).all()
        )
        if len(shifts) != len(shift_ids):
            raise ValidationAppError("Some shifts are invalid or not in this company")

        AssignmentService._validate_already_assigned(
            target_user_id=target_user_id,
            shift_ids=shift_ids
        )

        AssignmentService._validate_capacity(shifts=shifts)

        AssignmentService._validate_employee_shift_overlap(
            target_user_id=target_user_id,
            shifts=shifts
        )

        AssignmentService._validate_with_unavailability(
            company_id=company_id,
            target_user_id=target_user_id,
            shifts=shifts
        )

        for shift in shifts:
            assignment = ShiftAssignment(
                user_id=target_user_id,
                shift_id = shift.id,
                assigned_by=actor_user_id,
            )

            db.session.add(assignment)
        db.session.commit()

    @staticmethod
    def unassign_shift_to_user(*, company_id, actor_user_id, assignment_ids ):
        # TODO:
        # Prevent unassign when shift is locked or payroll period is frozen

        PermissionService.require_can_manage_company(
            company_id=company_id,
            user_id = actor_user_id,
        )

        assignments = (
            ShiftAssignment.query
            .join(Shift)
            .options(selectinload(ShiftAssignment.shift))
            .filter(
                ShiftAssignment.id.in_(assignment_ids),
                ShiftAssignment.deleted_at.is_(None),
                Shift.company_id == company_id
            ).all()
        )

        if not assignments:
            return
        
        if len(assignments) != len(assignment_ids):
            raise NotFoundError(message="Some assignments do not belong to this company")
        
        now = datetime.now(tz=UTC_TZ)

        for assignment in assignments:
            # TODO:
            # if assignment.shift.is_locked or payroll_frozen:

            assignment.deleted_at = now

        db.session.commit()


    @staticmethod
    def _is_time_overlap(start_a, end_a, start_b, end_b):
        return start_a < end_b and end_a > start_b

    @staticmethod
    def _validate_employee_shift_overlap(*, target_user_id, shifts):
        if not shifts:
            return

        shift_ids = [s.id for s in shifts]

        sorted_shifts = sorted(shifts, key=lambda s: s.start_at)
        for prev, curr in zip(sorted_shifts, sorted_shifts[1:]):
            if AssignmentService._is_time_overlap(prev.start_at, prev.end_at, curr.start_at, curr.end_at):
                raise ConflictError(
                    message="assignment.employee_shift_overlap",
                    details={"conflict_shift_ids": sorted([prev.id, curr.id])},
                )

        min_start = min(s.start_at for s in shifts)
        max_end = max(s.end_at for s in shifts)

        existing = (
            db.session.query(ShiftAssignment.shift_id, Shift.start_at, Shift.end_at)
            .join(Shift, Shift.id == ShiftAssignment.shift_id)
            .filter(
                ShiftAssignment.user_id == target_user_id,
                ShiftAssignment.deleted_at.is_(None),
                Shift.deleted_at.is_(None),
                Shift.end_at > min_start,
                Shift.start_at < max_end,
            )
        )

        if shift_ids:
            existing = existing.filter(ShiftAssignment.shift_id.notin_(shift_ids))

        existing = existing.all()

        conflict_shift_ids = []
        existing_conflict_shift_ids = []
        for shift in shifts:
            for ex_shift_id, ex_start, ex_end in existing:
                if AssignmentService._is_time_overlap(ex_start, ex_end, shift.start_at, shift.end_at):
                    conflict_shift_ids.append(shift.id)
                    existing_conflict_shift_ids.append(ex_shift_id)

        if conflict_shift_ids:
            raise ConflictError(
                message="assignment.employee_shift_overlap",
                details={
                    "conflict_shift_ids": sorted(set(conflict_shift_ids)),
                    "existing_conflict_shift_ids": sorted(set(existing_conflict_shift_ids)),
                },
            )

    @staticmethod
    def _validate_with_unavailability(*, company_id, target_user_id, shifts):
        if not shifts:
            return

        min_start = min(shift.start_at for shift in shifts)
        max_end = max(shift.end_at for shift in shifts)

        unavailabilities = (
            Unavailability.query.filter(
                Unavailability.company_id == company_id,
                Unavailability.user_id == target_user_id,
                Unavailability.deleted_at.is_(None),
                Unavailability.start_at < max_end,
                Unavailability.end_at > min_start,
            ).all()
        )

        conflict_shift_ids = []

        for shift in shifts:
            has_conflict = any(
                AssignmentService._is_time_overlap(
                    unavailability.start_at, unavailability.end_at,
                    shift.start_at, shift.end_at
                )
                for unavailability in unavailabilities
            )

            if has_conflict:
                conflict_shift_ids.append(shift.id)

        if conflict_shift_ids:
            raise ConflictError(
                message="assignment.unavailability_overlap",
                details={"conflict_shift_ids": sorted(conflict_shift_ids)},
            )

    @staticmethod
    def _validate_already_assigned(*, target_user_id, shift_ids):
        conflicts = (
            ShiftAssignment.query.filter(
                ShiftAssignment.user_id == target_user_id,
                ShiftAssignment.shift_id.in_(shift_ids),
                ShiftAssignment.deleted_at.is_(None)
            ).all()
        )

        if conflicts:
            conflict_shift_ids = [a.shift_id for a in conflicts]
            raise ConflictError(
                message="assignment.already_assigned",
                details={"conflict_shift_ids": sorted(conflict_shift_ids)},
        )
        
    @staticmethod
    def _validate_capacity(*, shifts):
        assignment_counts = (
            db.session.query(
                ShiftAssignment.shift_id,
                func.count(ShiftAssignment.id).label("count")
            ).filter(
                ShiftAssignment.shift_id.in_([s.id for s in shifts]),
                ShiftAssignment.deleted_at.is_(None)
            ).group_by(ShiftAssignment.shift_id)
            .all()
        )
        assignment_count_by_shift = {shift_id: cnt for shift_id, cnt in assignment_counts}

        over_capacity_shift_ids = []
        for shift in shifts:
            if assignment_count_by_shift.get(shift.id, 0) >= shift.capacity:
                over_capacity_shift_ids.append(shift.id)

        if over_capacity_shift_ids:
            raise ConflictError(
                message="assignment.capacity_exceeded",
                details={"conflict_shift_ids": sorted(over_capacity_shift_ids)},
            )






        
