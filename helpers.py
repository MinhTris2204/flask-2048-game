from flask import session
from game_logic import Game2048
from config import db, login_manager
from models import User


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return db.session.get(User, int(user_id))


def load_game() -> Game2048:
    """Load game state from session."""
    g = Game2048()
    state = session.get("game_state")
    if state:
        g.__dict__.update(state)
        # đảm bảo grid không bị mất
        g.grid = state.get("grid", g.grid)
    return g


def save_game(g: Game2048):
    """Save game state to session."""
    session["game_state"] = g.__dict__.copy()
    session["game_state"]["grid"] = g.grid
