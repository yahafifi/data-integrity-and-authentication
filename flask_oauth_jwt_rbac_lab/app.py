import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, get_jwt_identity
from authlib.integrations.flask_client import OAuth

from config import Config
from models import get_db, User
from auth_utils import (
    bcrypt,
    validate_password_policy,
    hash_password,
    check_password,
    generate_user_jwt,
    login_required_page,
    role_required_page,
)

app = Flask(__name__)
app.config.from_object(Config)

if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise RuntimeError("DATABASE_URL is missing. Copy .env.example to .env and set DATABASE_URL.")

db = get_db()
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_user():
    return {"current_user": session}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")

        if role not in ["student", "admin"]:
            role = "student"

        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("register"))

        is_valid, message = validate_password_policy(password)
        if not is_valid:
            flash(message, "danger")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("This email already exists. Please login.", "warning")
            return redirect(url_for("login"))

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            auth_provider="local",
            role=role,
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, auth_provider="local").first()
        if not user or not user.password_hash or not check_password(user.password_hash, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        token = generate_user_jwt(user)
        session["user_id"] = user.id
        session["name"] = user.name
        session["email"] = user.email
        session["role"] = user.role
        session["jwt_token"] = token
        session["auth_provider"] = user.auth_provider

        flash("Login successful. JWT generated.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/login/google")
def login_google():
    if not app.config["GOOGLE_CLIENT_ID"] or not app.config["GOOGLE_CLIENT_SECRET"]:
        flash("Google OAuth is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env.", "danger")
        return redirect(url_for("login"))

    redirect_uri = url_for("auth_google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/google/callback")
def auth_google_callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        user_info = google.userinfo()

    email = user_info.get("email", "").lower()
    name = user_info.get("name") or email.split("@")[0]

    if not email:
        flash("Could not retrieve email from Google.", "danger")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            password_hash=None,
            auth_provider="google",
            role="student",
        )
        db.session.add(user)
        db.session.commit()

    jwt_token = generate_user_jwt(user)
    session["user_id"] = user.id
    session["name"] = user.name
    session["email"] = user.email
    session["role"] = user.role
    session["jwt_token"] = jwt_token
    session["auth_provider"] = user.auth_provider

    flash("Google OAuth login successful. JWT generated.", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required_page
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
@role_required_page("admin")
def admin_panel():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin.html", users=users)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))
# API endpoint protected by JWT token.
# Test it using Postman:
# Authorization: Bearer <your-token>
@app.route("/api/profile")
@jwt_required()
def api_profile():
    user_id = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        "message": "This API is protected by JWT.",
        "user_id": user_id,
        "claims": {
            "name": claims.get("name"),
            "email": claims.get("email"),
            "role": claims.get("role"),
            "auth_provider": claims.get("auth_provider"),
        }
    })

@app.route("/api/admin")
@jwt_required()
def api_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Access denied. Admin role required."}), 403

    users = User.query.all()
    return jsonify({
        "message": "Admin API access granted.",
        "users": [u.to_dict() for u in users]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
