import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASS = os.getenv("DB_PASS", "admin_password")
    DB_NAME = os.getenv("DB_NAME", "inventory_db")
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9094")
    # Add Redis URL
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")