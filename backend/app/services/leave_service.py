from app.models import Leave
from app.services.companyUser_service import CompanyUserService
from app.services.datetimeRange_service import DateTimeRangeService
from app.services.permission_services import PermissionService
from app.domain.resolver import ReviewerResolver
from app.errors.error_base import NotFoundError, ValidationAppError, PermissionDeniedError

from app.extensions import db
from datetime import datetime
from app.config import UTC_TZ

class LeaveService:

  @staticmethod
  def create_leave(data, user_id, company_id):
    membership = PermissionService.require_active_member(
      company_id=company_id,
      user_id=user_id
    )
    
    assigned_reviewer_id = LeaveService.resolve_and_validate_reviewer(
      company_id=company_id,
      user_id=user_id,
      membership=membership,
      input_reviewer=data.get("assigned_reviewer_id")
    )
    
    start_at = data["start_at"].astimezone(UTC_TZ)
    end_at = data["end_at"].astimezone(UTC_TZ)

    LeaveService.validate_time_range(start_at, end_at)
    LeaveService.validate_no_time_conflicts(user_id, company_id, start_at, end_at)

    leave = Leave(
      user_id = user_id,
      company_id = company_id,
      start_at = start_at,
      end_at = end_at,
      leave_type = data['leave_type'],
      reason = data['reason'],
      assigned_reviewer_id = assigned_reviewer_id
    )
    db.session.add(leave)
    db.session.commit()
    return leave
  
  @staticmethod
  def list_leaves(user_id, company_id, scope="self"):

    PermissionService.require_active_member(
      company_id=company_id,
      user_id=user_id
    )

    query = (
      Leave.query.filter_by(company_id=company_id, deleted_at=None)
      .order_by(Leave.start_at)
    )

    if scope == "self":
      return query.filter_by(user_id= user_id).all()
    
    if scope == "all":
      PermissionService.can_view_all_leaves(company_id=company_id, user_id=user_id)
      return query.all()
    
    raise ValidationAppError("Invalid scope.")
  
  @staticmethod
  def get_leave(leave_id, company_id, user_id):
    leave = Leave.query.filter_by(
      id=leave_id,
      company_id=company_id,
      deleted_at=None
    ).first()

    if not leave:
      raise NotFoundError("Leave does not exist.")

    PermissionService.can_view_leave(
      company_id=company_id, 
      user_id=user_id, 
      leave=leave
    )

    return leave
  
  @staticmethod
  def update_leave(leave_id, user_id, company_id, data):
    try:
      leave = LeaveService.get_leave(leave_id, company_id, user_id)

      LeaveService.validate_creator(leave, user_id)

      if leave.status != "pending":
        raise PermissionDeniedError(message="Only pending leave can be updated")

      if leave.reviewed_at:
        raise PermissionDeniedError(message="Leave has already been reviewed.")

      membership = PermissionService.require_active_member(
        company_id=company_id,
        user_id=user_id
      )

      assigned_reviewer_id = LeaveService.resolve_and_validate_reviewer(
        company_id=company_id,
        user_id=user_id,
        membership=membership,
        input_reviewer=data.get("assigned_reviewer_id")
      )

      start_at = data["start_at"].astimezone(UTC_TZ)
      end_at = data["end_at"].astimezone(UTC_TZ)

      LeaveService.validate_time_range(start_at, end_at)
      LeaveService.validate_no_time_conflicts(user_id, company_id, start_at, end_at, exclude_id=leave_id)

      leave.start_at = start_at
      leave.end_at = end_at
      leave.leave_type = data["leave_type"]
      leave.reason = data["reason"]
      leave.assigned_reviewer_id = assigned_reviewer_id

      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def review_leave(leave_id, user_id, company_id, data):
    try:
      leave = LeaveService.get_leave(leave_id, company_id, user_id)

      membership = PermissionService.require_active_member(
        company_id=company_id,
        user_id=user_id
      )
      
      if not PermissionService.can_review(user_id, leave, membership):
        raise PermissionDeniedError(message="Insufficient permissions")
      
      if leave.status != "pending":
        raise PermissionDeniedError(message="Only pending leave can be reviewed.")
      
      if data.get("status") not in ("approved", "rejected"):
        raise ValidationAppError("Invalid review status")

      leave.status = data.get("status")
      leave.reject_reason = data.get("reject_reason")

      LeaveService.validate_reject_reason(data)
      
      # TODO: Handle impacted shift assignments after leave approval.
      # Possible follow-up actions include reassignment workflows,
      # notifications, or marking affected assignments for review.
      leave.reviewed_by = user_id
      leave.reviewed_at = datetime.now(tz=UTC_TZ)
      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def withdraw_leave(leave_id, user_id, company_id):
    try: 
      leave = LeaveService.get_leave(leave_id, company_id, user_id)
      LeaveService.validate_creator(leave, user_id)
      if leave.status == "withdrawn":
        raise ValidationAppError(message="Leave has already been withdrawn.")
      
      if leave.status != "pending":
        raise PermissionDeniedError(message="Only pending leave can be withdrawn.")

      leave.status = "withdrawn"
      db.session.commit()
      return True
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def validate_time_range(start_at, end_at):
    if start_at >= end_at:
      raise ValidationAppError("start_at must be earlier than end_at.")
  
  @staticmethod
  def validate_no_time_conflicts(user_id, company_id, start_at, end_at, exclude_id=None):
    if DateTimeRangeService.has_overlap(
      Leave,
      user_id=user_id,
      company_id=company_id,
      start_at=start_at,
      end_at=end_at,
      exclude_id=exclude_id
    ):
      raise ValidationAppError("Time range overlaps with existing Leave.")
  @staticmethod
  def validate_reject_reason(data):
    if data.get("status") == "rejected":
      if not data.get("reject_reason"):
        raise ValidationAppError("reject_reason is required when rejected")
    else:
      if data.get("reject_reason") not in (None, ""):
        raise ValidationAppError("reject_reason must be null when not rejected")

  @staticmethod
  def validate_creator(leave, user_id):
    if leave.user_id != user_id:
      raise PermissionDeniedError(message="Insufficient permissions")

  @staticmethod
  def resolve_and_validate_reviewer(*, company_id, user_id, membership, input_reviewer):
    assigned_reviewer_id = ReviewerResolver.resolve(user_id=user_id, input_reviewer=input_reviewer)

    reviewer_membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=assigned_reviewer_id)

    if not reviewer_membership:
      raise PermissionDeniedError(message="Reviewer is not a valid company member")

    PermissionService.validate_reviewer_assignment(membership, reviewer_membership)

    return assigned_reviewer_id