from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='../static')
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import models to ensure they are registered
    from app.models import User, Collection, CollectionPermission, TextureImage, ImageVersion
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Template context processor
    from app.utils.helpers import has_collection_permission
    @app.context_processor
    def utility_processor():
        return dict(has_collection_permission=has_collection_permission)
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
