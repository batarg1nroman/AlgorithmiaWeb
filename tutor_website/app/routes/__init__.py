# app/routes/__init__.py
# Импортируем модули роутеров для удобного доступа
from . import auth
from . import schedule
from . import homework
from . import ai_assistant
from . import knowledge_base
from . import notifications

__all__ = [
    "auth",
    "schedule",
    "homework",
    "ai_assistant",
    "knowledge_base",
    "notifications",
]
