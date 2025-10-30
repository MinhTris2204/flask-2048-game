"""
Main application entry point.
This file only initializes the app and runs the server.
All routes and models are defined in separate modules.
"""

import os
from config import app, db

# Import models first to ensure tables are defined
import models

# Import helpers to register user_loader
import helpers

# Import all routes (they register themselves with the app)
import routes.auth
import routes.game
import routes.premium
import routes.api

# Tạo tables ngay sau khi import models (cho Gunicorn)
# Chỉ chạy khi không phải local dev server
with app.app_context():
    try:
        db.create_all()
        print(">>> Tables created successfully")
    except Exception as e:
        print(f">>> Error creating tables: {e}")


@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print("DB ready.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Lấy PORT từ environment variable (Railway sẽ set)
    port = int(os.getenv("PORT", 5000))
    # Debug mode chỉ bật khi không phải production
    debug = os.getenv("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
