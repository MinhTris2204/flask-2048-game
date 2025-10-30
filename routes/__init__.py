from config import app


def register_routes():
    """Register all route blueprints."""
    # Import routes inside function to avoid circular imports
    from routes import auth, game, premium, api
    
    # Note: Since we're using direct routes instead of blueprints,
    # the routes are automatically registered when modules are imported
    pass
