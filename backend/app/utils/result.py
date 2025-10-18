from flask import jsonify

SUCCESS = 0
NO_AUTHORITY = -2
NO_LOGIN = -1
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

def success_res(data=None, message="OK", code=SUCCESS, status=200):
    return jsonify({
        "resultCode": code,
        "message": message,
        "data": data
    }), status

def error_res(message="Error", code=INTERNAL_SERVER_ERROR, status=400):
    return jsonify({
        "resultCode": code,
        "message": message,
        "data": None

    }), status