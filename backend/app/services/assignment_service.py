from app.extensions import db
from app.models import ShiftAssignment, Shift
from app.services.company_service import CompanyService
from app.services.companyUser_service import CompanyUserService
from app.errors.assignment import AssignmentConflictError, AssignmentCapacityExceededError

class AssignmentService:
    @staticmethod
    def assign_user_to_shifts(*, company_id, actor_user_id, target_user_id, shift_ids):
        CompanyService.get_company(company_id=company_id)

        CompanyUserService.require_manager(company_id=company_id, user_id=actor_user_id)

        user = CompanyUserService.get_active_membership(company_id=company_id, user_id=target_user_id)
        if not user:
            raise PermissionError("member doesn't exist")
        
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
        
        over_capacity_shift_ids = []
        for shift in shifts:
            count = (
                ShiftAssignment.query.filter(
                    ShiftAssignment.shift_id==shift.id,
                    ShiftAssignment.deleted_at.is_(None)
                ).count()
            )
        
            if count >= shift.capacity:
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
        print(">>> COMMITTING ASSIGNMENTS <<<")
        db.session.commit()





        
