import uuid
from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, render_template, session
from flask_login import login_required, current_user, login_user, logout_user
from config import app, db
from models import PremiumPlan, Order, User
from vnpay_config import VNPAY_TMN_CODE, VNPAY_HASH_SECRET, VNPAY_URL, VNPAY_RETURN_URL
from vnpay_helper import VNPay

# Khởi tạo VNPAY
vnpay = VNPay(VNPAY_TMN_CODE, VNPAY_HASH_SECRET, VNPAY_URL)


@app.route("/premium")
@login_required
def premium_packages():
    """Chuyển hướng đến trang quản lý Premium."""
    return redirect(url_for("premium_manage"))


@app.route("/premium/manage")
@login_required
def premium_manage():
    """Trang quản lý Premium."""
    current_user.check_premium_status()
    
    # Lấy các gói Premium có sẵn
    plans = PremiumPlan.query.filter_by(is_active=True).order_by(PremiumPlan.price).all()
    
    # Lấy lịch sử đơn hàng của user
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template("premium_manage.html", 
                         plans=plans, 
                         orders=orders,
                         is_premium=current_user.is_premium,
                         premium_expires_at=current_user.premium_expires_at)


@app.route("/payment/<int:plan_id>", methods=["GET", "POST"])
@login_required
def payment(plan_id):
    """Payment route for premium plans."""
    plan = PremiumPlan.query.get_or_404(plan_id)
    if not plan.is_active:
        flash("Gói này không còn khả dụng", "danger")
        return redirect(url_for("premium_manage"))
    
    # Convert plan price to float for template
    plan_price = float(plan.price)
    
    if request.method == "POST":
        payment_method = request.form.get("payment_method", "vnpay")
        
        if payment_method == "vnpay":
            # Set session permanent trước khi redirect để giữ session
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=7)
            
            # Tạo order pending
            order = Order(
                user_id=current_user.id,
                plan_id=plan.id,
                amount=plan.price,
                status="pending",
                payment_method="vnpay",
                transaction_id=str(uuid.uuid4())
            )
            db.session.add(order)
            db.session.commit()
            
            # Tạo URL thanh toán VNPay
            ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            order_info = f"Thanh toan goi Premium: {plan.name}"
            
            # Thời gian hết hạn (15 phút)
            expire_date = (datetime.now() + timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')
            
            vnpay_url = vnpay.create_payment_url(
                amount=float(plan.price),
                order_id=order.id,
                order_info=order_info,
                return_url=VNPAY_RETURN_URL,
                ip_addr=ip_addr,
                locale="vn",
                order_type="other",
                expire_date=expire_date
            )
            
            return redirect(vnpay_url)
        else:
            # Xử lý thanh toán mock khác
            # Calculate new expiration date
            if current_user.premium_expires_at and current_user.premium_expires_at > datetime.now():
                new_expires_at = current_user.premium_expires_at + timedelta(days=plan.duration_days)
            else:
                new_expires_at = datetime.now() + timedelta(days=plan.duration_days)
            
            order = Order(
                user_id=current_user.id,
                plan_id=plan.id,
                amount=plan.price,
                status="completed",
                payment_method=payment_method,
                transaction_id=str(uuid.uuid4()),
                completed_at=datetime.now()
            )
            db.session.add(order)
            
            current_user.is_premium = True
            current_user.premium_expires_at = new_expires_at
            db.session.commit()
            
            flash("Thanh toán thành công! Premium đã được kích hoạt.", "success")
            return redirect(url_for("game"))
    
    return render_template("payment.html", plan=plan, plan_price=plan_price)


@app.route("/vnpay_return")
def vnpay_return():
    """VNPay Return URL - Hiển thị kết quả thanh toán cho khách hàng"""
    # Lấy tất cả params từ VNPay
    vnp_params = {}
    for key, value in request.args.items():
        if key.startswith('vnp_'):
            vnp_params[key] = value
    
    # Kiểm tra checksum
    if not vnpay.verify_return(vnp_params.copy()):
        flash("Chữ ký không hợp lệ!", "danger")
        return redirect(url_for("game"))
    
    # Parse response
    result = vnpay.parse_response(vnp_params)
    
    # Kiểm tra kết quả thanh toán
    if result['response_code'] == '00' and result['transaction_status'] == '00':
        # Thanh toán thành công
        order_id = result['txn_ref']
        order = Order.query.get(order_id)
        
        if order and order.status == 'pending':
            plan = PremiumPlan.query.get(order.plan_id)
            user = User.query.get(order.user_id)
            
            if not user:
                flash("Không tìm thấy người dùng!", "danger")
                return redirect(url_for("game"))
            
            # Calculate premium expiration
            if user.premium_expires_at and user.premium_expires_at > datetime.now():
                new_expires_at = user.premium_expires_at + timedelta(days=plan.duration_days)
                duration_text = f"{plan.duration_days} ngày"
            else:
                new_expires_at = datetime.now() + timedelta(days=plan.duration_days)
                duration_text = f"{plan.duration_days} ngày"
            
            # Update order
            order.status = 'completed'
            order.completed_at = datetime.now()
            order.transaction_id = result['transaction_no']
            
            # Activate premium
            user.is_premium = True
            user.premium_expires_at = new_expires_at
            
            db.session.commit()
            
            # Đăng nhập user sau khi xử lý thanh toán để giữ session
            if not current_user.is_authenticated:
                login_user(user, remember=True)
                session.permanent = True
            elif current_user.id != user.id:
                # Nếu đang đăng nhập user khác, đăng xuất và đăng nhập user này
                logout_user()
                login_user(user, remember=True)
                session.permanent = True
            
            return render_template("payment_success.html", 
                                 plan_name=plan.name,
                                 duration=duration_text,
                                 amount=result['amount'],
                                 transaction_no=result['transaction_no'])
        else:
            flash("Đơn hàng không hợp lệ hoặc đã được xử lý!", "warning")
            return redirect(url_for("game"))
    else:
        # Thanh toán thất bại
        # Lấy thông tin order để đăng nhập lại user
        order_id = result.get('txn_ref')
        if order_id:
            order = Order.query.get(order_id)
            if order:
                user = User.query.get(order.user_id)
                if user:
                    # Đăng nhập lại user để giữ session
                    if not current_user.is_authenticated:
                        login_user(user, remember=True)
                        session.permanent = True
                    elif current_user.id != user.id:
                        logout_user()
                        login_user(user, remember=True)
                        session.permanent = True
                    
                    # Update order status
                    order.status = 'failed'
                    db.session.commit()
        
        error_messages = {
            '07': 'Giao dịch bị nghi ngờ gian lận',
            '09': 'Thẻ/Tài khoản chưa đăng ký InternetBanking',
            '10': 'Xác thực thông tin sai quá 3 lần',
            '11': 'Đã hết hạn chờ thanh toán',
            '12': 'Thẻ/Tài khoản bị khóa',
            '13': 'Sai mật khẩu OTP',
            '24': 'Khách hàng hủy giao dịch',
            '51': 'Tài khoản không đủ số dư',
            '65': 'Vượt quá hạn mức giao dịch trong ngày',
            '75': 'Ngân hàng đang bảo trì',
            '79': 'Sai mật khẩu quá số lần quy định',
            '99': 'Lỗi khác'
        }
        
        error_message = error_messages.get(result['response_code'], f"Mã lỗi: {result['response_code']}")
        
        return render_template("payment_error.html", 
                             error_message=error_message,
                             error_code=result['response_code'])


@app.route("/vnpay_ipn")
def vnpay_ipn():
    """VNPay IPN URL - Xử lý kết quả thanh toán từ VNPay (server-side)"""
    from flask import jsonify
    
    # Lấy tất cả params từ VNPay
    vnp_params = {}
    for key, value in request.args.items():
        if key.startswith('vnp_'):
            vnp_params[key] = value
    
    # Kiểm tra checksum
    if not vnpay.verify_return(vnp_params.copy()):
        return jsonify({'RspCode': '97', 'Message': 'Invalid signature'}), 200
    
    # Parse response
    result = vnpay.parse_response(vnp_params)
    
    # Tìm order
    order_id = result['txn_ref']
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'RspCode': '01', 'Message': 'Order not found'}), 200
    
    # Kiểm tra số tiền
    if float(order.amount) != result['amount']:
        return jsonify({'RspCode': '04', 'Message': 'Invalid amount'}), 200
    
    # Kiểm tra trạng thái
    if order.status != 'pending':
        return jsonify({'RspCode': '02', 'Message': 'Order already confirmed'}), 200
    
    # Xử lý kết quả
    if result['response_code'] == '00' and result['transaction_status'] == '00':
        # Thanh toán thành công
        plan = PremiumPlan.query.get(order.plan_id)
        user = User.query.get(order.user_id)
        
        if plan and user:
            # Calculate premium expiration
            if user.premium_expires_at and user.premium_expires_at > datetime.now():
                new_expires_at = user.premium_expires_at + timedelta(days=plan.duration_days)
            else:
                new_expires_at = datetime.now() + timedelta(days=plan.duration_days)
            
            # Update order
            order.status = 'completed'
            order.completed_at = datetime.now()
            order.transaction_id = result['transaction_no']
            
            # Activate premium
            user.is_premium = True
            user.premium_expires_at = new_expires_at
            
            db.session.commit()
            
            return jsonify({'RspCode': '00', 'Message': 'Success'}), 200
    
    # Thanh toán thất bại
    order.status = 'failed'
    db.session.commit()
    
    return jsonify({'RspCode': '00', 'Message': 'Confirmed'}), 200
