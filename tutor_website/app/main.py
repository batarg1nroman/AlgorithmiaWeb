from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime

from app.database import get_db, engine, Base
from app.models.user import User
from app.models.schedule import Schedule, RecurringSchedule
from app.models.homework import Homework
from app.config import settings
from app.utils.auth import get_current_user
from app.routes import auth, schedule, homework, ai_assistant, knowledge_base, notifications

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tutor Platform", version="1.0.0")

# Настройка статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(schedule.router)
app.include_router(homework.router)
app.include_router(ai_assistant.router)
app.include_router(knowledge_base.router)
app.include_router(notifications.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth/login")

    db = next(get_db())

    # Получаем ближайшие занятия
    upcoming_schedule = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.start_time > datetime.now()
    ).order_by(Schedule.start_time).limit(5).all()

    # Получаем последние задания
    if current_user.is_teacher:
        recent_homework = db.query(Homework).filter(
            Homework.teacher_id == current_user.id
        ).order_by(Homework.deadline.desc()).limit(5).all()
    else:
        recent_homework = db.query(Homework).filter(
            Homework.user_id == current_user.id
        ).order_by(Homework.deadline.desc()).limit(5).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": current_user,
            "upcoming_schedule": upcoming_schedule,
            "recent_homework": recent_homework
        }
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth/login")

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)