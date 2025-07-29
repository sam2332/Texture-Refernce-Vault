from .main import main_bp
from .auth import auth_bp
from .collections import collections_bp
from .images import images_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(collections_bp, url_prefix='/collection')
    app.register_blueprint(images_bp, url_prefix='/image')

__all__ = ['register_blueprints']
