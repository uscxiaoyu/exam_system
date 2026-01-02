from pydantic_settings import BaseSettings
import os
import json
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Grading System Pro"

    # Auth
    SECRET_KEY: str = "YOUR_SECRET_KEY_CHANGE_ME_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    # Database
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "grade_system"
    USE_SQLITE: bool = True

    # Storage
    STORAGE_TYPE: str = "local" # local, s3, minio
    STORAGE_LOCAL_PATH: str = "uploads"
    S3_BUCKET: str = "grade-bucket"
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./grade_system.db"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True
        env_file = ".env"

# Load settings
# Logic: Pydantic loads defaults and Env Vars.
# We then check for legacy db_config.json ONLY if we are in a local env (not container)
# or if specific critical env vars are not set.
# Ideally, we should migrate away from db_config.json entirely in favor of .env
DB_CONFIG_FILE = "backend/config/db_config.json"

def load_settings():
    settings = Settings()

    # Check if we are running in Docker (usually set by user or convention, but we can check if DB_HOST is 'db' or 'mysql')
    # Or simply: if DB_HOST is default 'localhost' AND json exists, maybe load json.
    # If DB_HOST is set via Env Var to something else, respect Env Var.

    # Check if env vars were actually loaded (checking against default)
    # This is tricky because "localhost" might be the intended env var.

    # Safe approach: Update settings from JSON only if JSON exists.
    # BUT, we must ensure JSON doesn't override Env Vars.
    # Since Pydantic BaseSettings are already loaded with Env Vars priority,
    # we should only update if the current value is the hardcoded default?
    # That's complex.

    # Better approach for this migration phase:
    # If DB_HOST env var is present, ignore JSON DB config.
    if "DB_HOST" in os.environ:
        return settings

    if os.path.exists(DB_CONFIG_FILE):
        try:
            with open(DB_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                # Only update if valid keys exist
                if "user" in data: settings.DB_USER = data["user"]
                if "password" in data: settings.DB_PASSWORD = data["password"]
                if "host" in data: settings.DB_HOST = data["host"]
                if "port" in data: settings.DB_PORT = int(data["port"])
                if "db_name" in data: settings.DB_NAME = data["db_name"]
        except Exception as e:
            print(f"Error loading config: {e}")

    return settings

settings = load_settings()
