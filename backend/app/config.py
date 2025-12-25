# config.py
class BaseConfig:
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY="your-super-secret-key"
    JWT_ALGORITHM = ""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///recipes.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.jpg', '.jpeg', '.png'}    

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DATABASE_URI = "sqlite:///recipes.db"

class ProductionConfig(BaseConfig):
    DATABASE_URI = "postgresql://user:password@localhost/prod_db"
