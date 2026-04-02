from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from app.utils.response import error
import logging
from app.errors.error_base import AppError
logger = logging.getLogger(__name__)


def register_error_handlers(app):

    # =========== Validation ============

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error(
            message="Validation error",
            status=400,
            details=err.messages,
        )
    # can be remove if no needed 
    @app.errorhandler(ValueError)
    def handle_value_error(err):
        return error(
            message=str(err),
            status=400,
        )
    
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return error(
            message=err.message,
            status=err.status_code,
            details=err.details,
        )

    # ============== HTTP errors ================

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return error(
            message=err.description,
            status=err.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Unhandled exception: %s", err)
        return error(
            message="Internal Server Error",
            status=500,
        )