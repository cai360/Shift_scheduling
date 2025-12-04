from flask import jsonify

SUCCESS = 0
NO_AUTHORITY = -2
NO_LOGIN = -1
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

def ok(data=None, status=200):
    return jsonify({"data": data}), status


def error(message, status=400, details=None):
    err = {"message": message}
    if details:
        err["details"] = details
    return jsonify({"error": err}), status