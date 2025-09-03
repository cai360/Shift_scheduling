from app.extensions import db

class Swap(db.Model):
    __tablename__ = 'swaps'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('shift_assignments.id', ondelete='CASCADE'), nullable=False)  # Fixed typo + CASCADE
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)  
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True) 
    cancelled = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    
    # Relationships
    shift_assignment = db.relationship(
        'ShiftAssignment', 
        back_populates='swaps'
    )

    requester = db.relationship(
        'User', 
        foreign_keys=[requester_id],
        back_populates='requested_swaps',
        overlaps="responder,responded_swaps"
    )
    
    responder = db.relationship(
        'User', 
        foreign_keys=[responder_id],
        back_populates='responded_swaps',
        overlaps="requester,requested_swaps"
    )
