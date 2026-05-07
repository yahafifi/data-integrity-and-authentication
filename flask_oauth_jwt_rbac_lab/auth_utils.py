import re
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

bcrypt = Bcrypt()

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)

def validate_password_policy(password: str):
    """
    Password must contain:
    - at least 8 characters
    - uppercase letter
    - lowercase letter
    - number
    - special character from @$!%*?&
    """
    if not password:
        return False, "Password is required."
    if not PASSWORD_REGEX.match(password):
        return False, "Password must be at least 8 chars and include uppercase, lowercase, number, and special character."
    return True, "Strong password."

def hash_password(password: str) -> str:
    return bcrypt.generate_password_hash(password).decode("utf-8")

def check_password(password_hash: str, password: str) -> bool:
    return bcrypt.check_password_hash(password_hash, password)

def generate_user_jwt(user):
    additional_claims = {
        "role": user.role,
        "email": user.email,
        "name": user.name,
        "auth_provider": user.auth_provider
    }
    return create_access_token(identity=str(user.id), additional_claims=additional_claims)

def login_required_page(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

def role_required_page(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if session.get("role") != required_role:
                flash("Access denied. Admin role required.", "danger")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
