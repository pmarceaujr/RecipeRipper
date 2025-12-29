# app/__init__.py
import os
from app.config import *
from flask import Flask
from .extensions import db, jwt, migrate, bcrypt, cors
from .auth.routes import auth_bp
from .recipes.routes import recipes_bp

def create_app():
    # Create app with instance folder support
    app = Flask(__name__, instance_relative_config=True)

    # Read environment variable (default to "development")
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Config for overrides and keeping secrets out of the codebase
    app.config.from_pyfile('config.py')  

    # Database configuration - use Heroku DATABASE_URL when present
    database_uri = os.environ.get('DATABASE_URL')
    if database_uri and database_uri.startswith("postgres://"):
        # Heroku uses "postgres://" but SQLAlchemy wants "postgresql://"
        database_uri = database_uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri or 'sqlite:///recipes.db'  # fallback for local
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    app.register_blueprint(recipes_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')    

    # Home route
    @app.route('/health')
    def home():
        return {"message": "The Recipe Ripper Database API", "status": "running"}

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Resource not found"}, 404

    @app.errorhandler(500)
    def internal_error(e):
        return {"error": "Internal server error"}, 500

    return app