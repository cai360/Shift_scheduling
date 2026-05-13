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
    # TODO : reviewed_by is required
    membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
    if not membership:
      raise Forbidden("User not in this company")
    
    reviewed_by = ReviewerResolver.resolve(
      user_id=user_id,
      company_id=company_id,
      input_reviewer=data.get("reviewed_by")
    )

    reviewer_membership = CompanyUserService.get_active_membership(
      company_id=company_id,
      user_id=reviewed_by
    )

    if not reviewer_membership:
      raise Forbidden("Reviewer is not a valid company member")

    PermissionService.validate_reviewer_assignment(
      membership,
      reviewer_membership
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

    membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

    if not membership:
      raise Forbidden("Not a company member.")

    query = (
      Leave.query.filter_by(company_id=company_id, deleted_at=None)
      .order_by(Leave.start_at)
    )

    if scope == "self":
      return query.filter_by(user_id= user_id).all()
    
    if scope == "all":
      if not PermissionService.require_can_manage_company(company_id=company_id, user_id=user_id):
        raise Forbidden("Insufficient permissions")
      return query.all()
    
    raise ValueError("Invalid scope.")
  
  @staticmethod
  def get_leave(leave_id, company_id, user_id):
    membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)
    if not membership:
      raise Forbidden("Not a company member.")
    
    leave = Leave.query.filter_by(
      id=leave_id,
      company_id=company_id,
      deleted_at=None
    ).first()

    if not leave:
      raise NotFound("Leave does not exist.")
    
    if leave.user_id == user_id:
      return leave
    
    if membership.role in ("manager", "owner"):
      return leave
    
    raise Forbidden("Insufficient permissions")
  
  @staticmethod
  def update_leave(leave_id, user_id, company_id, data):
    # TODO: Only creator can update & rejected_at is required can't update again
    try:
      leave = LeaveService.get_leave(leave_id, company_id, user_id)
      membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

      reviewed_by = ReviewerResolver.resolve(
        user_id=user_id,
        company_id=company_id,
        input_reviewer=data.get("reviewed_by")
      )
      
      reviewer_membership = CompanyUserService.get_active_membership(
        company_id=company_id,
        user_id=reviewed_by
      )

      # TODO: test only creator can update
      LeaveService.validate_creator(leave, user_id)

      if not reviewer_membership:
        raise Forbidden("Reviewer is not a valid company member")

      PermissionService.validate_reviewer_assignment(
        membership,
        reviewer_membership
      )

      if leave.status != "pending":
        raise Forbidden("Only pending leave can be updated")

      if leave.reviewed_at:
        raise Forbidden("Leave has already been reviewed.")

      start_at = data["start_at"].astimezone(UTC_TZ)
      end_at = data["end_at"].astimezone(UTC_TZ)

      LeaveService.validate_time_range(start_at, end_at)
      LeaveService.validate_no_time_conflicts(user_id, company_id, start_at, end_at, exclude_id=leave_id)

      leave.start_at = start_at
      leave.end_at = end_at
      leave.type = data["type"]
      leave.reason = data["reason"]
      leave.reviewed_by = reviewed_by
      # leave.reviewed_by = data["reviewed_by"]
      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  @staticmethod
  def review_leave(leave_id, user_id, company_id, data):
    # DONE: rejected_at is required can't review again
    try:
      leave = LeaveService.get_leave(leave_id, company_id, user_id)
      print("leave", leave)
      membership = CompanyUserService.get_active_membership(company_id=company_id, user_id=user_id)

      if not membership:
        raise Forbidden("Not a company member.")
      
      if not PermissionService.can_review(user_id, leave, membership):
        raise Forbidden("Insufficient permissions")

      # if leave.reviewed_at:
      #   raise Forbidden("Leave has already been reviewed.")
      
      if leave.status != "pending":
        raise Forbidden("Only pending leave can be reviewed.")
      
      if data["status"] not in ("approved", "rejected"):
        raise ValueError("Invalid review status")

      LeaveService.validate_reject_reason(data)

      leave.status = data["status"]
      leave.reject_reason = data["reject_reason"]
      
      leave.reviewed_at = datetime.now(tz=UTC_TZ)
      db.session.commit()
      return leave
    except Exception:
      db.session.rollback()
      raise
  
  # @staticmethod
  # def withdrawn_leave(leave_id, user_id, company_id, data):
  #   # TODO: add check for conflicts
  #   leave = Leave.query.get(leave_id)
  #   leave.status = data["status"]
  #   db.session.commit()
  #   return leave
  
  @staticmethod
  def delete_leave(leave_id, user_id, company_id):
    # DONE: rejected_at is required can't delete
    try: 
      leave = LeaveService.get_leave(leave_id, company_id, user_id)
      
      if (leave.user_id != user_id):
        raise Forbidden("Insufficient permissions")
      
      if leave.reviewed_at:
        raise Forbidden("Leave has already been reviewed and cannot be deleted.")
      
      if leave.status != "pending":
        raise Forbidden("Only pending leave can be deleted.")

      leave.deleted_at = datetime.now(tz=UTC_TZ)
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
      if data.get("reject_reason") is not None:
        raise ValueError("reject_reason must be null when not rejected")

  @staticmethod
  def validate_creator(leave, user_id):
    if leave.user_id != user_id:
      raise Forbidden("Insufficient permissions")