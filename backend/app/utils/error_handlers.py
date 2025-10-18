from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
from app.utils.result import error_res

def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return error_res(message=e.description, code=e.code, status=e.code)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return error_res(message=f"Validation error: {e.message}", code=400, status=400)
    
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        return error_res(message=str(e), code=400, status=400)
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception(e)
        return error_res(message="Internal Server Error", code=500, status=500)
    

