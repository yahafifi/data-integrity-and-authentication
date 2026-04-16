from flask import Blueprint, request, jsonify

from models.user_model import (
    get_user_by_username,
    get_user_by_email,
    create_user
)
from utils.auth_utils import (
    hash_password,
    verify_password,
    generate_token
)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"message": "no input data provided"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not username or not email or not password or not role:
        return jsonify({
            "message": "username, email, password, and role are required"
        }), 400

    if role not in ["admin", "student"]:
        return jsonify({
            "message": "role must be admin or student"
        }), 400

    if get_user_by_username(username):
        return jsonify({"message": "username already exists"}), 409

    if get_user_by_email(email):
        return jsonify({"message": "email already exists"}), 409

    password_hash = hash_password(password)
    create_user(username, email, password_hash, role)

    return jsonify({"message": "user created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "no input data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    user = get_user_by_username(username)

    if not user:
        return jsonify({"message": "invalid username or password"}), 401

    user_id = user[0]
    db_username = user[1]
    db_email = user[2]
    db_password_hash = user[3]
    db_role = user[4]

    if not verify_password(db_password_hash, password):
        return jsonify({"message": "invalid username or password"}), 401

    token = generate_token(user_id, db_username, db_email, db_role)

    return jsonify({
        "message": "login successful",
        "token": token,
        "expires_in_minutes": 30,
        "role": db_role
    }), 200