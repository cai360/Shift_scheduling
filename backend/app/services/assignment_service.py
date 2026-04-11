from app.extensions import db
from app.models import ShiftAssignment, Shift
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.services.permission_services import PermissionService
from app.errors.assignment import AssignmentConflictError, AssignmentCapacityExceededError
from datetime import datetime, timezone
from app.config import UTC_TZ
from sqlalchemy.orm import selectinload
from sqlalchemy import func

class AssignmentService:
    @staticmethod
    def assign_user_to_shifts(*, company_id, actor_user_id, target_user_id, shift_ids):
        CompanyService.get_company(company_id=company_id)

        PermissionService.require_can_manage_company(company_id=company_id, user_id=actor_user_id)

        user = CompanyUserService.get_active_membership(company_id=company_id, user_id=target_user_id)
        if not user:
            raise ValueError("member doesn't exist")
        
        shifts = (
            Shift.query
            .filter(
                Shift.company_id == company_id,
                Shift.id.in_(shift_ids),
                Shift.deleted_at.is_(None),
                Shift.published_at.isnot(None)
            ).all()
        )

        if len(shifts) != len(set(shift_ids)):
            raise ValueError("Some shifts are invalid, not published, or not in this company")
        
        conflicts = (
            ShiftAssignment.query.filter(
                ShiftAssignment.user_id == target_user_id,
                ShiftAssignment.shift_id.in_(shift_ids),
                ShiftAssignment.deleted_at.is_(None)
            ).all()
        )

        if conflicts:
            conflict_shift_ids = [a.shift_id for a in conflicts]
            raise AssignmentConflictError(conflict_shift_ids=conflict_shift_ids)
        
        count = (
            db.session.query(
                ShiftAssignment.shift_id,
                func.count(ShiftAssignment.id).label("count")
            ).filter(
                ShiftAssignment.shift_id.in_([s.id for s in shifts]),
                ShiftAssignment.deleted_at.is_(None)
            ).group_by(ShiftAssignment.shift_id)
            .all()
        )
    
        count_map = {shift_id: count for shift_id, count in count}
        over_capacity_shift_ids = []
        for shift in shifts:
            if count_map.get(shift.id, 0) >= shift.capacity:
                over_capacity_shift_ids.append(shift.id)

        if over_capacity_shift_ids:
            raise AssignmentCapacityExceededError(over_capacity_shift_ids)
            
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
            raise PermissionError("Some assignments do not belong to this company")
        
        now = datetime.now(tz=UTC_TZ)

        for assignment in assignments:
            # TODO:
            # if assignment.shift.is_locked or payroll_frozen:

            assignment.deleted_at = now

        db.session.commit()





        
