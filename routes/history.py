"""
Game History routes - Xem lại lịch sử chơi game
"""

from flask import render_template, request
from flask_login import login_required, current_user
from config import app, db
from models import Score
from sqlalchemy import desc


@app.route("/history")
@login_required
def game_history():
    """Hiển thị lịch sử chơi game của user"""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Lấy lịch sử scores của user hiện tại
    pagination = Score.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Score.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    scores = pagination.items
    
    # Tính toán thống kê
    total_games = Score.query.filter_by(user_id=current_user.id).count()
    
    if total_games > 0:
        best_score = db.session.query(db.func.max(Score.score))\
            .filter(Score.user_id == current_user.id).scalar() or 0
        
        best_tile = db.session.query(db.func.max(Score.max_tile))\
            .filter(Score.user_id == current_user.id).scalar() or 0
        
        avg_score = db.session.query(db.func.avg(Score.score))\
            .filter(Score.user_id == current_user.id).scalar() or 0
        
        total_moves = db.session.query(db.func.sum(Score.moves))\
            .filter(Score.user_id == current_user.id).scalar() or 0
    else:
        best_score = 0
        best_tile = 0
        avg_score = 0
        total_moves = 0
    
    stats = {
        'total_games': total_games,
        'best_score': int(best_score),
        'best_tile': int(best_tile),
        'avg_score': round(float(avg_score), 1),
        'total_moves': int(total_moves)
    }
    
    return render_template("game_history.html",
                         scores=scores,
                         stats=stats,
                         pagination=pagination)
