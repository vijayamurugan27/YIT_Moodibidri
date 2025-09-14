from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.views import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register CLI commands
    register_cli_commands(app)
    
    return app

def register_cli_commands(app):
    """Register custom CLI commands."""
    from app.commands import test_api
    app.cli.add_command(test_api)
