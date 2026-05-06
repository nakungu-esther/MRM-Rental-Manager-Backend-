from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # Database
    database_url: str = "mysql+pymysql://root:@localhost/rental_manager_db"

    # JWT
    secret_key: str = "change-me-in-production-use-long-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # File uploads
    upload_dir: str = "./uploads"

    # SMTP — fill these in your .env file
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_tls: bool = True
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()