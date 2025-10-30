from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import db


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    email = db.Column(db.String(120), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, pw: str):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, pw)
    
    def check_premium_status(self):
        """Kiểm tra premium có còn hiệu lực không."""
        if not self.is_premium or not self.premium_expires_at:
            return False
        if datetime.now() > self.premium_expires_at:
            self.is_premium = False
            db.session.commit()
            return False
        return True
    
    def get_premium_days_left(self):
        """Trả về số ngày premium còn lại."""
        if not self.premium_expires_at:
            return 0
        delta = self.premium_expires_at - datetime.now()
        return max(0, delta.days)


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_tile = db.Column(db.Integer, nullable=False)
    moves = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class PremiumPlan(db.Model):
    __tablename__ = "premium_plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("premium_plans.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    completed_at = db.Column(db.DateTime)
