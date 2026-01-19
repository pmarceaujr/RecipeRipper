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
    DATABASE_URL = "sqlite:///recipes.db"
    # SECRET_KEY=""   
    # JWT_SECRET_KEY=""
    # JWT_ALGORITHM=""
    # JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour in seconds
    # OPENAI_API_KEY=""
    # PORT=5000
    # UPLOAD_FOLDER="/uploads123"
    # AWS_ACCESS_KEY_ID=""
    # AWS_SECRET_ACCESS_KEY=""
    # AWS_DEFAULT_REGION=""
    # S3_BUCKET=""
    # DATABASE_URL=""


class ProductionConfig(BaseConfig):
    DATABASE_URL = "postgresql://user:password@localhost/prod_db"
