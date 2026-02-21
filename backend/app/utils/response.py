from flask import jsonify, make_response

SUCCESS = 0
NO_AUTHORITY = -2
NO_LOGIN = -1
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

def ok(data=None, status=200):
    resp = make_response({
        "success": True,
        "data": data
    }), status
    return resp
    # return jsonify({"data": data}), status


def error(message, status=400, details=None):
    err = {
        "success": False,
        "message": message
    }
    if details:
        err["details"] = details
    resp = make_response(jsonify(err), status)
    return resp
    # return jsonify({"error": err}), status