# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tutor_website.db")

    # Настройки приложения
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AI настройки (если используете)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Настройки email (если нужны уведомления)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")


settings = Settings()