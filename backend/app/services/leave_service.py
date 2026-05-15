from app.models import Leave
from app.models import ShiftAssignment
from app.models import Shift
from app.services.companyUser_service import CompanyUserService
from app.services.datetimeRange_service import DateTimeRangeService
from app.services.permission_services import PermissionService
from app.domain.resolver import ReviewerResolver

from app.extensions import db
from datetime import datetime

from werkzeug.exceptions import Forbidden, NotFound

from app.config import UTC_TZ
from uuid import UUID


class LeaveService:

  @staticmethod
  def create_leave(data, user_id, company_id):
    membership = PermissionService.require_roles(
      company_id=company_id,
      user_id=user_id,
      allowed_roles=("employee", "manager", "owner")
    )
    
    reviewed_by = LeaveService.resolve_and_validate_reviewer(
      company_id=company_id,
      user_id=user_id,
      membership=membership,
      input_reviewer=data.get("reviewed_by")
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
      type = data['type'],
      reason = data['reason'],
      reviewed_by = reviewed_by
    )
    db.session.add(leave)
    db.session.commit()
    return leave
  
  @staticmethod
  def list_leaves(user_id, company_id, scope="self"):

    PermissionService.require_roles(
      company_id=company_id,
      user_id=user_id,
      allowed_roles=("employee", "manager", "owner")
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
    
    raise ValueError("Invalid scope.")
  
  @staticmethod
  def get_leave(leave_id, company_id, user_id):
    leave = Leave.query.filter_by(
      id=leave_id,
      company_id=company_id,
      deleted_at=None
    ).first()

    if not leave:
      raise NotFound("Leave does not exist.")

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
        raise Forbidden("Only pending leave can be updated")

      if leave.reviewed_at:
        raise Forbidden("Leave has already been reviewed.")

      membership = PermissionService.require_roles(
        company_id=company_id,
        user_id=user_id,
        allowed_roles=("employee", "manager", "owner")
      )

      reviewed_by = LeaveService.resolve_and_validate_reviewer(
        company_id=company_id,
        user_id=user_id,
        membership=membership,
        input_reviewer=data.get("reviewed_by")
      )

      start_at = data["start_at"].astimezone(UTC_TZ)
      end_at = data["end_at"].astimezone(UTC_TZ)

      LeaveService.validate_time_range(start_at, end_at)
      LeaveService.validate_no_time_conflicts(user_id, company_id, start_at, end_at, exclude_id=leave_id)

      leave.start_at = start_at
      leave.end_at = end_at
      leave.type = data["type"]
      leave.reason = data["reason"]
      leave.reviewed_by = reviewed_by

      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def review_leave(leave_id, user_id, company_id, data):
    try:
      leave = LeaveService.get_leave(leave_id, company_id, user_id)

      membership = PermissionService.require_roles(
        company_id=company_id,
        user_id=user_id,
        allowed_roles=("employee", "manager", "owner")
      )
      if not membership:
        raise Forbidden("Not a company member.")
      
      if not PermissionService.can_review(user_id, leave, membership):
        raise Forbidden("Insufficient permissions")
      
      if leave.status != "pending":
        raise Forbidden("Only pending leave can be reviewed.")
      
      if data["status"] not in ("approved", "rejected"):
        raise ValueError("Invalid review status")


      leave.status = data["status"]
      leave.reject_reason = data["reject_reason"]

      LeaveService.validate_reject_reason(data)
      
      leave.reviewed_at = datetime.now(tz=UTC_TZ)
      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def delete_leave(leave_id, user_id, company_id):
    try: 
      leave = LeaveService.get_leave(leave_id, company_id, user_id)
      LeaveService.validate_creator(leave, user_id)
      
      if leave.status != "pending":
        raise Forbidden("Only pending leave can be deleted.")

      leave.deleted_at = datetime.now(tz=UTC_TZ)
      leave.status = "withdrawn"
      db.session.commit()
      return True
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def validate_time_range(start_at, end_at):
    if start_at >= end_at:
      raise ValueError("start_at must be earlier than end_at.")
  
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
      raise ValueError("Time range overlaps with existing Leave.")
  @staticmethod
  def validate_reject_reason(data):
    if data.get("status") == "rejected":
      if not data.get("reject_reason"):
        raise ValueError("reject_reason is required when rejected")
    else:
      if data.get("reject_reason") != "":
        raise ValueError("reject_reason must be null when not rejected")

  @staticmethod
  def validate_creator(leave, user_id):
    if leave.user_id != user_id:
      raise Forbidden("Insufficient permissions")

  @staticmethod
  def resolve_and_validate_reviewer(*, company_id, user_id, membership, input_reviewer):
    reviewed_by = ReviewerResolver.resolve(user_id=user_id, input_reviewer=input_reviewer)

    reviewer_membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=reviewed_by)

    if not reviewer_membership:
      raise Forbidden("Reviewer is not a valid company member")

    PermissionService.validate_reviewer_assignment(membership, reviewer_membership)

    return reviewed_by