class AppError(Exception):
    status_code = 400
   
    def __init__(self, message="Application error", details=None):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class PermissionDeniedError(AppError):
    status_code = 403


class ConflictError(AppError):
    status_code = 409


class ValidationAppError(AppError):
    status_code = 400

class UnauthorizedError(AppError):
    status_code = 401