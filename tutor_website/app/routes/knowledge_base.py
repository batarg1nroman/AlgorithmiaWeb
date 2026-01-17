# app/routes/knowledge_base.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Простая база знаний в памяти (в реальном приложении использовать БД)
KNOWLEDGE_BASE = {
    "math": {
        "title": "Математика",
        "topics": [
            {"id": 1, "name": "Алгебра", "description": "Уравнения, функции, неравенства"},
            {"id": 2, "name": "Геометрия", "description": "Фигуры, теоремы, построения"},
            {"id": 3, "name": "Тригонометрия", "description": "Синусы, косинусы, тангенсы"},
            {"id": 4, "name": "Математический анализ", "description": "Производные, интегралы, пределы"}
        ],
        "articles": [
            {"id": 1, "title": "Квадратные уравнения", "content": "ax² + bx + c = 0, D = b² - 4ac", "topic": "Алгебра"},
            {"id": 2, "title": "Теорема Пифагора", "content": "a² + b² = c²", "topic": "Геометрия"},
            {"id": 3, "title": "Производная", "content": "f'(x) = lim(h→0) [f(x+h)-f(x)]/h",
             "topic": "Математический анализ"}
        ]
    },
    "physics": {
        "title": "Физика",
        "topics": [
            {"id": 1, "name": "Механика", "description": "Движение, силы, энергия"},
            {"id": 2, "name": "Электричество", "description": "Ток, напряжение, сопротивление"},
            {"id": 3, "name": "Оптика", "description": "Свет, линзы, отражение"}
        ],
        "articles": [
            {"id": 1, "title": "Законы Ньютона",
             "content": "1. Тело сохраняет состояние... 2. F=ma 3. Действие равно противодействию",
             "topic": "Механика"},
            {"id": 2, "title": "Закон Ома", "content": "I = U/R", "topic": "Электричество"}
        ]
    },
    "programming": {
        "title": "Программирование",
        "topics": [
            {"id": 1, "name": "Python", "description": "Язык программирования высокого уровня"},
            {"id": 2, "name": "Алгоритмы", "description": "Структуры данных и алгоритмы"},
            {"id": 3, "name": "Веб-разработка", "description": "HTML, CSS, JavaScript"}
        ],
        "articles": [
            {"id": 1, "title": "Основы Python", "content": "Переменные, циклы, условия, функции", "topic": "Python"},
            {"id": 2, "title": "Сортировка пузырьком", "content": "Простой алгоритм сортировки", "topic": "Алгоритмы"}
        ]
    }
}


@router.get("/", response_class=HTMLResponse)
async def knowledge_base_home(request: Request):
    """Главная страница базы знаний"""
    return templates.TemplateResponse(
        "knowledge_base/topics.html",
        {
            "request": request,
            "subjects": KNOWLEDGE_BASE.keys()
        }
    )


@router.get("/{subject}", response_class=HTMLResponse)
async def subject_page(
        request: Request,
        subject: str,
        topic: Optional[str] = None
):
    """Страница предмета"""
    if subject not in KNOWLEDGE_BASE:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    subject_data = KNOWLEDGE_BASE[subject]

    # Фильтруем статьи по теме если указана
    articles = subject_data["articles"]
    if topic:
        articles = [a for a in articles if a["topic"].lower() == topic.lower()]

    return templates.TemplateResponse(
        "knowledge_base/subject.html",
        {
            "request": request,
            "subject": subject,
            "subject_data": subject_data,
            "articles": articles,
            "selected_topic": topic
        }
    )


@router.get("/article/{subject}/{article_id}", response_class=HTMLResponse)
async def article_page(
        request: Request,
        subject: str,
        article_id: int
):
    """Страница статьи"""
    if subject not in KNOWLEDGE_BASE:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    article = None
    for art in KNOWLEDGE_BASE[subject]["articles"]:
        if art["id"] == article_id:
            article = art
            break

    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    return templates.TemplateResponse(
        "knowledge_base/article.html",
        {
            "request": request,
            "subject": subject,
            "article": article
        }
    )


@router.get("/api/search")
async def search_articles(
        q: str = Query(..., min_length=2),
        subject: Optional[str] = None
):
    """Поиск по базе знаний"""
    results = []

    for subj_key, subj_data in KNOWLEDGE_BASE.items():
        if subject and subj_key != subject:
            continue

        for article in subj_data["articles"]:
            if (q.lower() in article["title"].lower() or
                    q.lower() in article["content"].lower() or
                    q.lower() in article["topic"].lower()):
                results.append({
                    "subject": subj_key,
                    "subject_title": subj_data["title"],
                    **article
                })

    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


@router.get("/api/subjects")
async def get_subjects():
    """Получить список предметов"""
    subjects = []
    for key, data in KNOWLEDGE_BASE.items():
        subjects.append({
            "id": key,
            "title": data["title"],
            "topic_count": len(data["topics"]),
            "article_count": len(data["articles"])
        })

    return {"subjects": subjects}


@router.get("/api/{subject}/topics")
async def get_subject_topics(subject: str):
    """Получить темы предмета"""
    if subject not in KNOWLEDGE_BASE:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    return {"topics": KNOWLEDGE_BASE[subject]["topics"]}


@router.post("/api/add-article")
async def add_article(
        subject: str = Form(...),
        title: str = Form(...),
        content: str = Form(...),
        topic: str = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Добавить статью (только для авторизованных)"""
    if subject not in KNOWLEDGE_BASE:
        raise HTTPException(status_code=400, detail="Неверный предмет")

    # Генерируем ID
    new_id = max([a["id"] for a in KNOWLEDGE_BASE[subject]["articles"]], default=0) + 1

    article = {
        "id": new_id,
        "title": title,
        "content": content,
        "topic": topic,
        "author": current_user.username,
        "created_at": db.func.now()
    }

    KNOWLEDGE_BASE[subject]["articles"].append(article)

    return JSONResponse({
        "message": "Статья добавлена",
        "article_id": new_id
    })