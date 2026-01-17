# app/database.py (с поддержкой конфигурации)
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class DatabaseConfig:
    """Конфигурация базы данных"""

    # Получаем URL из переменных окружения или используем SQLite по умолчанию
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        # SQLite по умолчанию для разработки
        DATABASE_URL = "sqlite:///./tutor_website.db"
        print("⚠️  DATABASE_URL не указан, используется SQLite по умолчанию")

    # Определяем параметры подключения в зависимости от типа БД
    CONNECT_ARGS = {}
    if DATABASE_URL.startswith("sqlite"):
        CONNECT_ARGS = {"check_same_thread": False}

    # Настройки пула подключений
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))


# Создаем движок базы данных с настройками
engine = create_engine(
    DatabaseConfig.DATABASE_URL,
    connect_args=DatabaseConfig.CONNECT_ARGS,
    pool_size=DatabaseConfig.POOL_SIZE,
    max_overflow=DatabaseConfig.MAX_OVERFLOW,
    pool_timeout=DatabaseConfig.POOL_TIMEOUT,
    pool_recycle=DatabaseConfig.POOL_RECYCLE,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true"  # Логирование SQL запросов
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Позволяет использовать объекты после коммита
)

# Базовый класс для всех моделей
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость FastAPI для получения сессии базы данных.

    Пример использования:
    ```python
    from fastapi import Depends
    from app.database import get_db
    from sqlalchemy.orm import Session

    @app.get("/items/")
    async def read_items(db: Session = Depends(get_db)):
        items = db.query(Item).all()
        return items
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Инициализация базы данных.
    Создает все таблицы, определенные в моделях.

    Вызывать при запуске приложения.
    """
    try:
        # Импортируем все модели, чтобы они зарегистрировались у Base
        from app.models import user, schedule, homework, notification
        print("📋 Загружены модели:", [user, schedule, homework, notification])

        # Создаем таблицы
        Base.metadata.create_all(bind=engine)
        print(f"✅ База данных инициализирована: {DatabaseConfig.DATABASE_URL}")

    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        raise


def test_connection() -> bool:
    """Проверить подключение к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False


# Экспортируем основные объекты
__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "test_connection"
]

# Автоматическая инициализация при импорте (опционально)
if __name__ == "__main__":
    # Тестируем при прямом запуске
    if test_connection():
        init_db()
        print("🎉 База данных готова к работе!")