# config.py
class BaseConfig:
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY="your-super-secret-key"
    JWT_ALGORITHM = ""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///recipes123.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads66'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.jpg', '.jpeg', '.png'}    

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DATABASE_URI = "sqlite:///recipes1234.db"
    # SECRET_KEY="super-secret-key123"   
    # JWT_SECRET_KEY="this-is-the-real-super-secret-key123"
    # JWT_ALGORITHM="HS256"
    # JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour in seconds
    # OPENAI_API_KEY="123sk-proj-4IQsDF3QHY4GGxJoDz2zEZ3RLVEaC2Cqmqx8jgNeKX1mrzpPlhA6tnH5WTSKz3UwpcAeFq1Ym2T3BlbkFJr84hQGNSY8k2g38OL9vrH9IHcl0wDquwaUv2NrRuG0t3EMEGEj8AAKpnzZ1CjUwEKkfxxvSi8A"
    # PORT=5000
    # UPLOAD_FOLDER="/uploads123"
    # AWS_ACCESS_KEY_ID="AKIA5VLOXNVZSXJJTEWU123"
    # AWS_SECRET_ACCESS_KEY="KUjwPFNON5tGdHJ3mu/GMwAJanUZm4wm42dFoU7U123"
    # AWS_DEFAULT_REGION="us-east-1123"
    # S3_BUCKET="recipe-database-text-extractor-bucket123"
    # DATABASE_URL="123postgres://u7nvu2k5qfam92:p743e7d65c3bb14d9752f8b326e789e483acd51dce2680699e3f3c59194653c3e@ccu6unqr99fgui.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d138rer8c2bapn"


class ProductionConfig(BaseConfig):
    DATABASE_URI = "postgresql://user:password@localhost/prod_db"
