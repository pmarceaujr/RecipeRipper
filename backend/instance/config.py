# instance/config.py
SECRET_KEY = "super-secret-key"   
JWT_SECRET_KEY="this-is-the-real-super-secret-key"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour in seconds
OPENAI_API_KEY="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"
PORT=5000
UPLOAD_FOLDER="/uploads"
AWS_ACCESS_KEY_ID="AKIA5VLOXNVZSXJJTEWU"
AWS_SECRET_ACCESS_KEY="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"
AWS_DEFAULT_REGION="us-east-1"
S3_BUCKET="recipe-database-text-extractor-bucket"
# DATABASE_URL="sqlite:///recipes.db"
# DATABASE_URI = "postgresql://user:password@localhost/secure_db"
