import app.models.leaves as Leave
from app.extensions import db

class LeaveService:

  @staticmethod
  def create_leave(user_id, company_id, start_date, end_date, type, reason, reviewed_by):
    leave = Leave(
      user_id = user_id,
      company_id = company_id,
      start_date = start_date,
      end_date = end_date,
      type = type,
      reason = reason,
      reviewed_by = reviewed_by
    )
    db.session.add(leave)
    db.session.commit()
    return leave
  
  @staticmethod
  def list_leaves(user_id, company_id):
    return Leave.query.filter(
      Leave.company_id == company_id, 
      Leave.user_id == user_id
    ).all()
  
  @staticmethod
  def get_leave(leave_id):
    return Leave.query.get(leave_id)
  
  @staticmethod
  def update_leave(leave_id, start_date, end_date, type, reason, reviewed_by):
    leave = Leave.query.get(leave_id)
    leave.start_date = start_date
    leave.end_date = end_date
    leave.type = type
    leave.reason = reason
    leave.reviewed_by = reviewed_by
    db.session.commit()
    return leave
  
  @staticmethod
  def delete_leave(leave_id):
    leave = Leave.query.get(leave_id)
    db.session.delete(leave)
    db.session.commit()
    return leave