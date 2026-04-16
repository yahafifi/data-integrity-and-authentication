from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from models.user_model import get_user_by_id

protected_bp = Blueprint("protected_bp", __name__)


@protected_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"message": "user not found"}), 404

    return jsonify({
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "role": user[3],
        "created_at": str(user[4])
    }), 200


@protected_bp.route("/student-area", methods=["GET"])
@jwt_required()
def student_area():
    claims = get_jwt()
    role = claims.get("role")

    if role != "student":
        return jsonify({"message": "access denied: students only"}), 403

    return jsonify({
        "message": f"welcome {claims.get('username')} to the student area"
    }), 200


@protected_bp.route("/admin-area", methods=["GET"])
@jwt_required()
def admin_area():
    claims = get_jwt()
    role = claims.get("role")

    if role != "admin":
        return jsonify({"message": "access denied: admins only"}), 403

    return jsonify({
        "message": f"welcome {claims.get('username')} to the admin area"
    }), 200