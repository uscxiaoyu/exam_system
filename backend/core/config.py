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
    USE_SQLITE: bool = True # For now default to SQLite due to env limitations

    # Storage
    STORAGE_TYPE: str = "local" # local or s3
    STORAGE_LOCAL_PATH: str = "uploads"
    S3_BUCKET: str = ""
    S3_REGION: str = ""
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None # For MinIO

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./grade_system.db"
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True

# Load from existing json if present, otherwise use defaults
DB_CONFIG_FILE = "backend/config/db_config.json"
def load_settings():
    settings = Settings()
    if os.path.exists(DB_CONFIG_FILE):
        try:
            with open(DB_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                settings.DB_USER = data.get("user", settings.DB_USER)
                settings.DB_PASSWORD = data.get("password", settings.DB_PASSWORD)
                settings.DB_HOST = data.get("host", settings.DB_HOST)
                settings.DB_PORT = int(data.get("port", settings.DB_PORT))
                settings.DB_NAME = data.get("db_name", settings.DB_NAME)
        except Exception as e:
            print(f"Error loading config: {e}")
    return settings

settings = load_settings()
