from flask import redirect, url_for, render_template, session
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_
from config import app, db
from models import Score, User
from game_logic import Game2048
from helpers import save_game


@app.route("/")
def home():
    """Home route - redirect to game or login."""
    if current_user.is_authenticated:
        return redirect(url_for("game"))
    return redirect(url_for("login"))


@app.route("/game")
@login_required
def game():
    """Main game route."""
    current_user.check_premium_status()
    if "game_state" not in session:
        g = Game2048()
        g.setup()
        save_game(g)
    return render_template("game.html", 
                           username=current_user.username,
                           is_premium=current_user.is_premium)


@app.route("/leaderboard")
def leaderboard():
    """Leaderboard route."""
    best_per_user = (
        db.session.query(
            Score.user_id.label("user_id"),
            func.max(Score.score).label("best_score")
        )
        .group_by(Score.user_id)
        .subquery()
    )

    rows = (
        db.session.query(Score, User.username)
        .join(best_per_user, and_(
            Score.user_id == best_per_user.c.user_id,
            Score.score == best_per_user.c.best_score
        ))
        .join(User, User.id == Score.user_id)
        .order_by(
            desc(Score.score),
            desc(Score.max_tile),
            Score.moves.asc(),
            Score.created_at.asc()
        )
        .limit(20)
        .all()
    )

    return render_template("leaderboard.html", rows=rows)
