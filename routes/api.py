import uuid
from flask import request, jsonify, session
from flask_login import login_required, current_user
from config import app, db
from models import Score, Order
from game_logic import Game2048
from helpers import load_game, save_game


@app.route("/api/load_game", methods=["GET"])
@login_required
def load_current_game():
    """API endpoint to load current game state."""
    if "game_state" not in session:
        # Nếu không có game state, tạo game mới
        g = Game2048()
        result = g.setup()
        save_game(g)
        return jsonify({"ok": True, **result, "can_undo": False})
    
    # Load game hiện tại
    g = load_game()
    return jsonify({
        "ok": True,
        "grid": g.grid,
        "score": g.score,
        "moves": g.moves,
        "can_undo": g.last_state is not None
    })


@app.route("/api/start_game", methods=["POST"])
@login_required
def start_game():
    """API endpoint to start a new game."""
    g = Game2048()
    result = g.setup()
    save_game(g)
    return jsonify({"ok": True, **result, "can_undo": False})


@app.route("/api/move", methods=["POST"])
@login_required
def move():
    """API endpoint to make a move in the game."""
    if "game_state" not in session:
        return jsonify({"ok": False, "message": "Chưa khởi tạo trò chơi"}), 400

    payload = request.get_json(silent=True) or {}
    direction = payload.get("direction")
    if direction not in ("up", "down", "left", "right"):
        return jsonify({"ok": False, "message": "Hướng không hợp lệ"}), 400

    g = load_game()
    result = g.move(direction)

  
    resp = {"ok": True, **result, "can_undo": g.last_state is not None}

    if result.get("changed"):
    
        save_game(g)
     
        over = g.check_game_over() 
        if over:
           
            score_entry = Score(
                user_id=current_user.id,
                score=g.score,
                max_tile=g.max_tile(),
                moves=g.moves
            )
            db.session.add(score_entry)
            db.session.commit()
           
            session.pop("game_state", None)
            resp["game_over"] = over
    else:
       
        save_game(g)

    return jsonify(resp)


@app.route("/api/undo", methods=["POST"])
@login_required
def undo():
    """API endpoint to undo the last move."""
    if "game_state" not in session:
        return jsonify({"ok": False, "message": "Chưa khởi tạo trò chơi"}), 400

    g = load_game()
    result = g.undo()
    save_game(g) 
    return jsonify({"ok": True, **result, "can_undo": False})


@app.route("/api/submit_score", methods=["POST"])
@login_required
def submit_score():
    """API endpoint to submit a score."""
    payload = request.get_json(silent=True) or {}
    try:
        score = int(payload.get("score", 0))
        max_tile = int(payload.get("max_tile", 2))
        moves = int(payload.get("moves", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Payload không hợp lệ"}), 400

    if score < 0 or max_tile < 2 or moves < 0:
        return jsonify({"ok": False, "message": "Giá trị không hợp lệ"}), 400

    s = Score(user_id=current_user.id, score=score, max_tile=max_tile, moves=moves)
    db.session.add(s)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/me")
@login_required
def me():
    """API endpoint to get current user info."""
    current_user.check_premium_status()
    return jsonify({
        "id": current_user.id, 
        "username": current_user.username,
        "is_premium": current_user.is_premium,
        "premium_days_left": current_user.get_premium_days_left(),
        "premium_expires_at": current_user.premium_expires_at.strftime("%Y-%m-%d %H:%M:%S") if current_user.premium_expires_at else None
    })


@app.route("/api/premium/cancel", methods=["POST"])
@login_required
def cancel_premium():
    """API endpoint to cancel Premium subscription."""
    current_user.check_premium_status()
    
    if not current_user.is_premium:
        return jsonify({"ok": False, "message": "Bạn chưa có Premium để hủy"}), 400
    
    # Ghi lại lịch sử hủy Premium vào orders
    cancel_order = Order(
        user_id=current_user.id,
        plan_id=None,
        amount=0,
        status="cancelled",
        payment_method="manual_cancel",
        transaction_id=str(uuid.uuid4())
    )
    db.session.add(cancel_order)
    
    # Hủy Premium ngay lập tức
    current_user.is_premium = False
    current_user.premium_expires_at = None
    
    db.session.commit()
    
    return jsonify({"ok": True, "message": "Premium đã được hủy thành công"})


@app.route("/api/premium/hint", methods=["POST"])
@login_required
def hint():
    """API endpoint to get game hint (premium feature)"""
    current_user.check_premium_status()
    if not current_user.is_premium:
        return jsonify({"ok": False, "message": "Chức năng premium. Vui lòng nâng cấp!"}), 403
    
    if "game_state" not in session:
        return jsonify({"ok": False, "message": "Chưa khởi tạo trò chơi"}), 400
    
    g = load_game()
    result = g.get_hint()
    if result:
        save_game(g)
        return jsonify({"ok": True, "direction": result.get("direction")})
    
    return jsonify({"ok": False, "message": "Không có gợi ý"}), 400


@app.route("/api/premium/shuffle", methods=["POST"])
@login_required
def shuffle():
    """API endpoint to shuffle board (premium feature)"""
    current_user.check_premium_status()
    if not current_user.is_premium:
        return jsonify({"ok": False, "message": "Chức năng premium. Vui lòng nâng cấp!"}), 403
    
    if "game_state" not in session:
        return jsonify({"ok": False, "message": "Chưa khởi tạo trò chơi"}), 400
    
    g = load_game()
    result = g.shuffle()
    save_game(g)
    return jsonify({"ok": True, "grid": result.get("grid")})


@app.route("/api/premium/swap", methods=["POST"])
@login_required
def swap_tiles():
    """API endpoint to swap two tiles (premium feature)"""
    current_user.check_premium_status()
    if not current_user.is_premium:
        return jsonify({"ok": False, "message": "Chức năng premium. Vui lòng nâng cấp!"}), 403
    
    if "game_state" not in session:
        return jsonify({"ok": False, "message": "Chưa khởi tạo trò chơi"}), 400
    
    data = request.get_json()
    row1 = data.get("row1")
    col1 = data.get("col1")
    row2 = data.get("row2")
    col2 = data.get("col2")
    
    if row1 is None or col1 is None or row2 is None or col2 is None:
        return jsonify({"ok": False, "message": "Thiếu tham số"}), 400
    
    g = load_game()
    result = g.swap_two_tiles(row1, col1, row2, col2)
    
    if result.get("ok"):
        save_game(g)
    
    return jsonify(result)
