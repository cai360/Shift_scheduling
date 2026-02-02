# app/utils/error_handlers.py
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from flask import jsonify
from app.utils.response import error
import logging
from app.errors.assignment import AssignmentConflictError, AssignmentCapacityExceededError

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error(
            message="Validation error",
            status=400,
            details=err.messages
        )
    
    @app.errorhandler(PermissionError)
    def handle_permission_error(err):
        return error(
            message=str(err),
            status=403
        )

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        return error(
            message=str(err),
            status=400
        )

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception(err)  
        return error(
            message="Internal Server Error",
            status=500,
            details=str(err)
        )
    
    @app.errorhandler(AssignmentConflictError)
    def handle_assignment_conflict(err):
        return error(
            message="Assignment conflict",
            status=409,
            details={
                "conflict_shift_ids": err.conflict_shift_ids
            }
        )
    

    @app.errorhandler(AssignmentCapacityExceededError)
    def handle_assignment_capacity_exceeded(err):
        return error(
            message="Shift capacity exceeded",
            status=409,
            details={
                "shift_ids": err.shift_ids
            },
        )
