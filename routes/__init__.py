from flask import Blueprint
from .home_routes import home_bp
from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .logout_routes import logout_bp

def init_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(logout_bp)
