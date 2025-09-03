from flask import Blueprint, jsonify, request

bp = Blueprint("shifts", __name__, url_prefix="/shifts")


@bp.get("/ping")
def ping():
    return jsonify({"message": "pong shifts"})