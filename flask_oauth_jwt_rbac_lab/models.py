from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

_db = SQLAlchemy()

def get_db():
    return _db

class User(_db.Model):
    __tablename__ = "users"

    id = _db.Column(_db.Integer, primary_key=True)
    name = _db.Column(_db.String(120), nullable=False)
    email = _db.Column(_db.String(255), unique=True, nullable=False, index=True)
    password_hash = _db.Column(_db.String(255), nullable=True)
    auth_provider = _db.Column(_db.String(30), nullable=False, default="local")  # local/google
    role = _db.Column(_db.String(30), nullable=False, default="student")       # student/admin
    created_at = _db.Column(_db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "auth_provider": self.auth_provider,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }
