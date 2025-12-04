# app/utils/error_handlers.py
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    ...
    # @app.errorhandler(HTTPException)
    # def handle_http_exception(e: HTTPException):
    #     status = getattr(e, "code", 500) or 500
    #     desc = getattr(e, "description", "HTTP error")
    #     return error_res(message=desc, code=status, status=status)

    # @app.errorhandler(ValidationError)
    # def handle_validation_error(e: ValidationError):
    #     app.logger.debug("ValidationError: %s", e.messages)
    #     return error_res(
    #         message="Validation error",
    #         code=400,
    #         status=400,
    #         errors=e.messages 
    #     )

    # @app.errorhandler(ValueError)
    # def handle_value_error(e: ValueError):
    #     return error_res(message=str(e), code=400, status=400)

    # @app.errorhandler(Exception)
    # def handle_unexpected_error(e: Exception):
    #     app.logger.exception(e)  
    #     return error_res(message="Internal Server Error", code=500, status=500)