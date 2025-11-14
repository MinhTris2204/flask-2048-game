import uuid
from datetime import datetime, timedelta
from flask import request, redirect, url_for, flash, render_template, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from config import app, db
from models import PremiumPlan, Order, User
from payos_config import PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY, PAYOS_RETURN_URL, PAYOS_CANCEL_URL
from payos_helper import PayOS

# Khởi tạo PayOS helper (tự implement - đã cải thiện signature generation)
payos = PayOS(PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY)


@app.route("/payos/cancel")
def payos_cancel():
    """PayOS Cancel URL - Người dùng hủy thanh toán"""
    order_code = request.args.get('orderCode')
    
    if order_code:
        order = Order.query.get(int(order_code))
        if order and order.status == 'pending':
            order.status = 'cancelled'
            db.session.commit()
            
            # Render payment error page với script thoát iframe
            return render_template("payment_error.html",
                                 error_message="Bạn đã hủy thanh toán",
                                 error_code="CANCELLED",
                                 break_iframe=True)
    
    # Nếu không có order_code hoặc order không tìm thấy
    flash("Không tìm thấy thông tin đơn hàng!", "warning")
    return redirect(url_for("premium_manage"))


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
        payment_method = request.form.get("payment_method", "payos")
        
        if payment_method == "payos":
            # Set session permanent trước khi redirect để giữ session
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=7)
            
            # Tạo order pending
            order = Order(
                user_id=current_user.id,
                plan_id=plan.id,
                amount=plan.price,
                status="pending",
                payment_method="payos",
                transaction_id=str(uuid.uuid4())
            )
            db.session.add(order)
            db.session.commit()
            
            # Tạo payment link PayOS
            try:
                # Description tối đa 25 ký tự theo yêu cầu PayOS
                description = f"Premium {plan.duration_days}d"  # VD: "Premium 365d" = 13 ký tự
                
                print(f">>> Creating PayOS link for order {order.id}, amount {plan.price}")
                
                result = payos.create_payment_link(
                    order_code=order.id,
                    amount=int(plan.price),
                    description=description,
                    return_url=PAYOS_RETURN_URL,
                    cancel_url=PAYOS_CANCEL_URL,
                    buyer_name=None,
                    buyer_email=None
                )
                
                print(f">>> PayOS Response: {result}")
                
                # Kiểm tra lỗi từ PayOS
                if result.get("code") != "00" and result.get("code") != "200":
                    error_desc = result.get("desc", "Unknown error")
                    print(f">>> PayOS Error: {result.get('code')} - {error_desc}")
                    flash(f"Lỗi PayOS: {error_desc}", "danger")
                    return redirect(url_for("premium_manage"))
                
                if "error" in result:
                    print(f">>> PayOS Error: {result.get('error')}")
                    flash("Không thể tạo link thanh toán. Vui lòng thử lại!", "danger")
                    return redirect(url_for("premium_manage"))
                
                # Lấy checkout URL - kiểm tra data không None
                data = result.get("data")
                if not data:
                    print(f">>> No data in PayOS response: {result}")
                    flash("Không thể tạo link thanh toán. Vui lòng thử lại!", "danger")
                    return redirect(url_for("premium_manage"))
                
                payment_url = data.get("checkoutUrl")
                if not payment_url:
                    print(f">>> No checkoutUrl in response data: {result}")
                    flash("Không thể tạo link thanh toán. Vui lòng thử lại!", "danger")
                    return redirect(url_for("premium_manage"))
                
                print(f">>> Redirecting to PayOS checkout URL: {payment_url}")
                # Redirect trực tiếp đến trang thanh toán PayOS
                return redirect(payment_url)
                
            except Exception as e:
                print(f">>> EXCEPTION in payment creation: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                flash("Có lỗi xảy ra. Vui lòng thử lại!", "danger")
                return redirect(url_for("premium_manage"))
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


@app.route("/payos/return")
def payos_return():
    """PayOS Return URL - Hiển thị kết quả thanh toán cho khách hàng"""
    # Lấy params từ PayOS
    code = request.args.get('code')
    order_code = request.args.get('orderCode')
    cancel = request.args.get('cancel', 'false').lower() == 'true'
    status = request.args.get('status', 'PENDING')
    
    if not order_code:
        flash("Không tìm thấy thông tin đơn hàng!", "danger")
        return redirect(url_for("game"))
    
    # Kiểm tra kết quả thanh toán
    if code == '00' and status == 'PAID' and not cancel:
        # Thanh toán thành công
        order = Order.query.get(int(order_code))
        
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
            # transaction_id đã được set khi tạo order
            
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
                                 amount=float(order.amount),
                                 transaction_no=order.transaction_id,
                                 break_iframe=True)
        else:
            flash("Đơn hàng không hợp lệ hoặc đã được xử lý!", "warning")
            return redirect(url_for("game"))
    else:
        # Thanh toán thất bại hoặc bị hủy
        order = Order.query.get(int(order_code))
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
                if cancel:
                    order.status = 'cancelled'
                else:
                    order.status = 'failed'
                db.session.commit()
        
        if cancel:
            error_message = "Bạn đã hủy thanh toán"
        elif status == 'CANCELLED':
            error_message = "Giao dịch đã bị hủy"
        elif status == 'PENDING':
            error_message = "Giao dịch đang chờ xử lý"
        else:
            error_message = f"Thanh toán thất bại - Trạng thái: {status}"
        
        return render_template("payment_error.html", 
                             error_message=error_message,
                             error_code=code or status,
                             break_iframe=True)


@app.route("/payos/webhook", methods=["POST"])
def payos_webhook():
    """PayOS Webhook - Xử lý kết quả thanh toán từ PayOS (server-side)"""
    # Lấy webhook data từ PayOS
    webhook_data = request.get_json()
    
    if not webhook_data:
        return jsonify({"error": "No data"}), 400
    
    # Verify signature
    if not payos.verify_webhook_signature(webhook_data):
        print(">>> PayOS Webhook: Invalid signature")
        return jsonify({"error": "Invalid signature"}), 400
    
    # Parse webhook data
    code = webhook_data.get('code')
    data = webhook_data.get('data', {})
    order_code = data.get('orderCode')
    
    if not order_code:
        return jsonify({"error": "Missing orderCode"}), 400
    
    # Tìm order
    order = Order.query.get(order_code)
    
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    # Kiểm tra số tiền
    if int(order.amount) != data.get('amount'):
        return jsonify({"error": "Invalid amount"}), 400
    
    # Kiểm tra trạng thái
    if order.status != 'pending':
        return jsonify({"success": True, "message": "Order already processed"}), 200
    
    # Xử lý kết quả
    if code == '00' and data.get('code') == '00':
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
            order.transaction_id = data.get('reference', order.transaction_id)
            
            # Activate premium
            user.is_premium = True
            user.premium_expires_at = new_expires_at
            
            db.session.commit()
            
            print(f">>> PayOS Webhook: Order {order_code} completed successfully")
            return jsonify({"success": True, "message": "Payment completed"}), 200
    
    # Thanh toán thất bại
    order.status = 'failed'
    db.session.commit()
    
    print(f">>> PayOS Webhook: Order {order_code} failed")
    return jsonify({"success": True, "message": "Payment failed"}), 200
