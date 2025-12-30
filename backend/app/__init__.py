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

    print(f"DB URL: {os.environ.get('DATABASE_URL')} or {app.config.get('DATABASE_URL')}")
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    app.config.from_pyfile('config.py', silent=True)

    app.config.update({
        # Security / Auth
        'SECRET_KEY': os.environ.get('SECRET_KEY') or app.config.get('SECRET_KEY'),
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY') or app.config.get('JWT_SECRET_KEY'),
        'JWT_ALGORITHM': os.environ.get('JWT_ALGORITHM') or app.config.get('JWT_ALGORITHM'), 
        'JWT_ACCESS_TOKEN_EXPIRES': int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)) or app.config.get('JWT_ACCESS_TOKEN_EXPIRES'),

        # OpenAI / AI services
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY') or app.config.get('OPENAI_API_KEY'),

        # Server / Flask
        'PORT': os.environ.get('PORT')  or app.config.get('PORT'),

        # File upload
        'UPLOAD_FOLDER': os.environ.get('UPLOAD_FOLDER')  or app.config.get('UPLOAD_FOLDER'),  # /tmp is safe on Heroku

        # AWS / S3
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID')  or app.config.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY') or app.config.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_DEFAULT_REGION': os.environ.get('AWS_DEFAULT_REGION') or app.config.get('AWS_DEFAULT_REGION'),
        'S3_BUCKET': os.environ.get('S3_BUCKET') or app.config.get('S3_BUCKET'),

        # Database (most important on Heroku!)
        'DATABASE_URL': os.environ.get('DATABASE_URL') or app.config.get('DATABASE_URL'),
        # Very important: Heroku forces SSL on Postgres
        # 'SQLALCHEMY_ENGINE_OPTIONS': {'connect_args': {'sslmode': 'require'}} if 'DATABASE_URL' in os.environ else None,
    })

    # ───────────────────────────────────────────────
    # Option A – Most readable
    print("┌──────────── Loaded config from────────────┐")
    for key, value in sorted(app.config.items()):
        if not key.isupper(): continue           # skip Flask internal stuff
        print(f"│ {key: <28} : {value!r}")
    print("└────────────────────────────────────────────────────────────┘")


 # Use Postgres on Heroku, SQLite locally
    # print(f"database url123: {DATABASE_URL}")
    DATABASE_URL = app.config.get('DATABASE_URL')
    print(f"database url: {DATABASE_URL}")

    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        # Heroku provides "postgres://" but SQLAlchemy wants "postgresql://"
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or "sqlite:///recipes.db"
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