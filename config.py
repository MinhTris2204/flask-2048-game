import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

load_dotenv()

# Khởi tạo Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "devsecret")

# --- Database URL from env ---
db_url = os.getenv("DATABASE_URL")  # >>> PHẢI LÀ TÊN NÀY <<<
if not db_url:
    # Chỉ fallback SQLite nếu KHÔNG có env (tránh override)
    db_url = "sqlite:///game2048.db"

# Chuẩn hoá scheme MySQL
if db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": 5,
    "max_overflow": 10,
}
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Google OAuth configuration
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID", "")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Khởi tạo extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={
        'scope': 'openid email profile',
        'token_endpoint_auth_method': 'client_secret_post',
    },
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
)

# (Tùy chọn) In ra loại DB để debug (không in password)
safe_url = db_url.split("@")[-1] if "@" in db_url else db_url
print(">>> Using DB:", ("mysql+pymysql://***@" + safe_url) if "mysql" in db_url else db_url)

# Tạo bảng lần đầu (an toàn)
with app.app_context():
    try:
        db.create_all()
        print(">>> DB create_all done")
    except Exception as e:
        print(">>> DB init warning:", e)
