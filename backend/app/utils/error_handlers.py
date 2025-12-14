# app/utils/error_handlers.py
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from flask import jsonify
from app.utils.response import error
import logging

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