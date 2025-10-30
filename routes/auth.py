from flask import request, redirect, url_for, flash, render_template, session
from flask_login import login_user, login_required, logout_user
from config import app, db, google
from models import User


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration route."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Vui lòng nhập đủ thông tin.", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại.", "warning")
            return redirect(url_for("register"))

        u = User(username=username)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect(url_for("login"))
    return render_template("auth_register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            # Set session permanent để duy trì session lâu hơn
            session.permanent = True
            return redirect(url_for("game"))
        flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")
        return redirect(url_for("login"))
    return render_template("auth_login.html")


@app.route("/logout")
@login_required
def logout():
    """User logout route."""
    logout_user()
    session.pop("game_state", None)
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("login"))


@app.route("/login/google")
def google_login():
    """Bắt đầu quá trình đăng nhập Google OAuth."""
    # Kiểm tra Google OAuth có được config không
    if not app.config["GOOGLE_CLIENT_ID"] or not app.config["GOOGLE_CLIENT_SECRET"]:
        flash("Google Login chưa được cấu hình. Vui lòng liên hệ admin.", "warning")
        return redirect(url_for("login"))
    
    redirect_uri = url_for("google_callback", _external=True)
    return google.authorize_redirect(redirect_uri, prompt='select_account')


@app.route("/login/google/callback")
def google_callback():
    """Xử lý callback từ Google OAuth."""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash("Không thể lấy thông tin từ Google.", "danger")
            return redirect(url_for("login"))
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0] if email else 'user')
        
        # Tìm user theo google_id
        user = User.query.filter_by(google_id=google_id).first()
        
        if user:
            # User đã tồn tại, đăng nhập
            login_user(user, remember=True)
            flash(f"Chào mừng {user.username}!", "success")
            return redirect(url_for("game"))
        else:
            # Kiểm tra email đã tồn tại chưa
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                # Link Google account với account hiện có
                existing_user.google_id = google_id
                if not existing_user.email:
                    existing_user.email = email
                db.session.commit()
                login_user(existing_user, remember=True)
                flash(f"Đã liên kết tài khoản Google với {existing_user.username}!", "success")
                return redirect(url_for("game"))
            
            # Tạo username unique từ email hoặc name
            base_username = name.replace(' ', '_').lower()
            username = base_username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Tạo user mới
            new_user = User(
                username=username,
                email=email,
                google_id=google_id
            )
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash(f"Tài khoản mới đã được tạo! Chào mừng {username}!", "success")
            return redirect(url_for("game"))
            
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash("Có lỗi xảy ra khi đăng nhập với Google.", "danger")
        return redirect(url_for("login"))
