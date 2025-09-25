import os
from dotenv import load_dotenv

load_dotenv()

class Config: 
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )

    # Make sure to ping the database connection before using it to prevent "lost connection" errors
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Docs told me to do this to reduce overhead since Flask-SQLAlchemy inherently tracks changes to DB models and emits signals
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

    # CORS since frontend and backend are two different ports during development
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
     DEBUG = False
