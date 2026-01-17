# app/routes/ai_assistant.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os

from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Папка для истории чатов
CHAT_HISTORY_DIR = "uploads/chat_histories"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


# Простой AI (заглушка) - в реальном приложении подключите OpenAI API
class SimpleAI:
    @staticmethod
    def generate_response(user_message: str, context: dict = None) -> str:
        """Генерирует ответ на сообщение пользователя"""
        # Простые правила для демонстрации
        user_message_lower = user_message.lower()

        responses = {
            "привет": "Привет! Я ваш AI-ассистент для учебы. Чем могу помочь?",
            "как дела": "У меня все отлично! Готов помочь вам с учебой.",
            "помощь": "Я могу помочь с:\n1. Объяснением тем\n2. Решением задач\n3. Планированием учебы\n4. Ответами на вопросы",
            "математика": "Математика - это интересно! Какая тема вас интересует?",
            "физика": "Физика изучает законы природы. Что конкретно хотите узнать?",
            "программирование": "Программирование - создание инструкций для компьютера. Какой язык вас интересует?",
            "спасибо": "Всегда пожалуйста! Обращайтесь, если нужна помощь.",
            "пока": "До свидания! Удачи в учебе!",
        }

        # Ищем ключевую фразу
        for key, response in responses.items():
            if key in user_message_lower:
                return response

        # Если не нашли подходящий ответ
        return f"Я получил ваше сообщение: '{user_message}'. В настоящее время я обучаюсь и могу помочь с базовыми вопросами по учебе. Задайте вопрос по математике, физике или программированию!"


@router.get("/", response_class=HTMLResponse)
async def ai_assistant_page(request: Request):
    """Страница AI ассистента"""
    return templates.TemplateResponse("ai_assistant.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """Страница чата с AI"""
    # Загружаем историю чата пользователя
    history_file = os.path.join(CHAT_HISTORY_DIR, f"user_{current_user.id}.json")
    chat_history = []

    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
        except:
            chat_history = []

    return templates.TemplateResponse(
        "ai_assistant/chat.html",
        {
            "request": request,
            "chat_history": chat_history[-20:]  # Последние 20 сообщений
        }
    )


@router.post("/chat/send")
async def send_message(
        request: Request,
        message: str = Form(...),
        current_user: User = Depends(get_current_user)
):
    """Отправить сообщение AI"""
    if not message.strip():
        return JSONResponse({"error": "Сообщение не может быть пустым"})

    # Загружаем историю
    history_file = os.path.join(CHAT_HISTORY_DIR, f"user_{current_user.id}.json")
    chat_history = []

    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
        except:
            chat_history = []

    # Добавляем сообщение пользователя
    user_msg = {
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    }
    chat_history.append(user_msg)

    # Получаем ответ от AI
    ai_response = SimpleAI.generate_response(message)

    # Добавляем ответ AI
    ai_msg = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now().isoformat()
    }
    chat_history.append(ai_msg)

    # Сохраняем историю (ограничиваем размер)
    if len(chat_history) > 100:  # Максимум 100 сообщений
        chat_history = chat_history[-100:]

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

    return JSONResponse({
        "user_message": message,
        "ai_response": ai_response,
        "timestamp": datetime.now().isoformat()
    })


@router.get("/chat/history")
async def get_chat_history(
        limit: int = 50,
        current_user: User = Depends(get_current_user)
):
    """Получить историю чата"""
    history_file = os.path.join(CHAT_HISTORY_DIR, f"user_{current_user.id}.json")

    if not os.path.exists(history_file):
        return {"messages": [], "count": 0}

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
    except:
        chat_history = []

    # Ограничиваем количество
    recent_history = chat_history[-limit:] if len(chat_history) > limit else chat_history

    return {
        "messages": recent_history,
        "count": len(recent_history),
        "total": len(chat_history)
    }


@router.delete("/chat/clear")
async def clear_chat_history(
        current_user: User = Depends(get_current_user)
):
    """Очистить историю чата"""
    history_file = os.path.join(CHAT_HISTORY_DIR, f"user_{current_user.id}.json")

    if os.path.exists(history_file):
        os.remove(history_file)

    return {"message": "История чата очищена"}


@router.get("/help/{subject}")
async def get_ai_help(
        subject: str,
        topic: str = None,
        current_user: User = Depends(get_current_user)
):
    """Получить помощь по предмету"""
    # База знаний для разных предметов
    knowledge_base = {
        "math": {
            "algebra": "Алгебра изучает операции над числами и переменными. Основные темы: уравнения, неравенства, функции.",
            "geometry": "Геометрия изучает формы и их свойства. Основные темы: треугольники, окружности, теорема Пифагора.",
            "calculus": "Математический анализ изучает изменения. Основные темы: производные, интегралы, пределы.",
            "default": "Математика - это наука о числах, формах и структурах. Какой раздел вас интересует: алгебра, геометрия или математический анализ?"
        },
        "physics": {
            "mechanics": "Механика изучает движение тел. Законы Ньютона: 1) Тело сохраняет состояние покоя или равномерного движения, 2) F=ma, 3) Действие равно противодействию.",
            "electricity": "Электричество изучает электрические заряды и ток. Закон Ома: I=U/R.",
            "thermodynamics": "Термодинамика изучает тепло и энергию. Первый закон: энергия сохраняется.",
            "default": "Физика изучает законы природы. Какой раздел вас интересует: механика, электричество или термодинамика?"
        },
        "programming": {
            "python": "Python - язык программирования высокого уровня. Используется для веб-разработки, анализа данных, AI.",
            "javascript": "JavaScript - язык для веб-разработки. Работает в браузере и на сервере (Node.js).",
            "algorithms": "Алгоритмы - последовательность шагов для решения задачи. Важные темы: сортировка, поиск, структуры данных.",
            "default": "Программирование - создание инструкций для компьютера. Какой язык или тему изучаете?"
        }
    }

    subject_data = knowledge_base.get(subject.lower())
    if not subject_data:
        return {"error": f"Предмет '{subject}' не найден в базе знаний"}

    if topic:
        response = subject_data.get(topic.lower(), subject_data["default"])
    else:
        response = subject_data["default"]

    return {
        "subject": subject,
        "topic": topic,
        "response": response
    }


@router.post("/explain")
async def explain_topic(
        request: Request,
        topic: str = Form(...),
        level: str = Form("beginner"),
        current_user: User = Depends(get_current_user)
):
    """Объяснить тему на определенном уровне"""
    explanations = {
        "квадратное уравнение": {
            "beginner": "Квадратное уравнение выглядит так: ax² + bx + c = 0. Решается через дискриминант: D = b² - 4ac.",
            "intermediate": "Корни квадратного уравнения: x = (-b ± √D) / 2a. Дискриминант определяет количество корней: D>0 - два корня, D=0 - один корень, D<0 - нет действительных корней.",
            "advanced": "Квадратное уравнение можно решать через теорему Виета: для x² + px + q = 0 сумма корней = -p, произведение = q. Также можно выделить полный квадрат."
        },
        "производная": {
            "beginner": "Производная показывает скорость изменения функции. Например, скорость - производная от пути.",
            "intermediate": "Производная функции f(x) в точке x: f'(x) = lim(h→0) [f(x+h)-f(x)]/h. Основные правила: (xⁿ)' = n*xⁿ⁻¹, (sin x)' = cos x.",
            "advanced": "Производная - линейный оператор. Правила: сумма, произведение, частное, цепное правило. Геометрически - тангенс угла наклона касательной."
        }
    }

    topic_lower = topic.lower()
    if topic_lower in explanations:
        explanation = explanations[topic_lower].get(level, explanations[topic_lower]["beginner"])
    else:
        explanation = f"Тема '{topic}' на уровне '{level}'. Рекомендую обратиться к учебнику или преподавателю."

    return JSONResponse({
        "topic": topic,
        "level": level,
        "explanation": explanation
    })