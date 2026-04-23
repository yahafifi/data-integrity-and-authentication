from flask import Flask, render_template, request, redirect, session, url_for
import pyotp
import qrcode
import os

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

# Fake database for teaching only
users = {}


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return "User already exists!"

        # Generate secret for Google Authenticator
        secret = pyotp.random_base32()

        users[username] = {
            "password": password,
            "secret": secret,
            "is_2fa_enabled": False
        }

        session["temp_user"] = username
        return redirect(url_for("setup_2fa"))

    return render_template("register.html")


@app.route("/setup_2fa")
def setup_2fa():
    username = session.get("temp_user")
    if not username or username not in users:
        return redirect(url_for("register"))

    secret = users[username]["secret"]

    # Create provisioning URI
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name="Flask2FADemo")

    # Generate QR code
    qr_path = os.path.join("static", f"{username}_qr.png")
    os.makedirs("static", exist_ok=True)

    img = qrcode.make(uri)
    img.save(qr_path)

    return render_template("setup_2fa.html", username=username, qr_path=qr_path, secret=secret)


@app.route("/confirm_2fa", methods=["POST"])
def confirm_2fa():
    username = session.get("temp_user")
    code = request.form["code"]

    if not username or username not in users:
        return redirect(url_for("register"))

    secret = users[username]["secret"]
    totp = pyotp.TOTP(secret)

    if totp.verify(code):
        users[username]["is_2fa_enabled"] = True
        session.pop("temp_user", None)
        return redirect(url_for("login"))
    else:
        return "Invalid code. Try again."


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users.get(username)

        if not user or user["password"] != password:
            return "Invalid username or password"

        session["pending_user"] = username

        if user["is_2fa_enabled"]:
            return redirect(url_for("verify_2fa"))
        else:
            session["user"] = username
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    username = session.get("pending_user")

    if not username or username not in users:
        return redirect(url_for("login"))

    if request.method == "POST":
        code = request.form["code"]
        secret = users[username]["secret"]
        totp = pyotp.TOTP(secret)

        if totp.verify(code):
            session["user"] = username
            session.pop("pending_user", None)
            return redirect(url_for("dashboard"))
        else:
            return "Invalid 2FA code"

    return render_template("verify_2fa.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)