# app/routes/schedule.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.schedule import Schedule, RecurringSchedule, ScheduleStatus
from app.utils.auth import get_current_user
from app.utils.notifications import NotificationManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def schedule_page(
        request: Request,
        date: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Страница расписания"""
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()

        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Получаем занятия пользователя на день
        lessons = db.query(Schedule).filter(
            Schedule.student_id == current_user.id,
            Schedule.start_time >= start_of_day,
            Schedule.start_time < end_of_day
        ).order_by(Schedule.start_time).all()

        # Получаем регулярные занятия
        recurring = db.query(RecurringSchedule).filter(
            RecurringSchedule.student_id == current_user.id,
            RecurringSchedule.is_active == True
        ).all()

        return templates.TemplateResponse(
            "schedule/schedule.html",
            {
                "request": request,
                "lessons": lessons,
                "recurring": recurring,
                "current_date": target_date,
                "prev_date": (target_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                "next_date": (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
            }
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты")


@router.get("/manage", response_class=HTMLResponse)
async def manage_schedule(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Управление расписанием"""
    # Получаем все будущие занятия
    lessons = db.query(Schedule).filter(
        Schedule.student_id == current_user.id,
        Schedule.start_time > datetime.now()
    ).order_by(Schedule.start_time).all()

    # Получаем все регулярные занятия
    recurring = db.query(RecurringSchedule).filter(
        RecurringSchedule.student_id == current_user.id
    ).all()

    return templates.TemplateResponse(
        "schedule/manage_schedule.html",
        {
            "request": request,
            "lessons": lessons,
            "recurring": recurring
        }
    )


@router.get("/add", response_class=HTMLResponse)
async def add_lesson_page(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """Страница добавления занятия"""
    # По умолчанию следующая дата и время
    default_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    default_time = "10:00"

    return templates.TemplateResponse(
        "schedule/add_lesson.html",
        {
            "request": request,
            "default_date": default_date,
            "default_time": default_time
        }
    )


@router.post("/add")
async def add_lesson(
        request: Request,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        date: str = Form(...),
        start_time: str = Form(...),
        duration: int = Form(60),
        teacher_id: int = Form(...),  # В реальном приложении выбирать из списка
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Добавление нового занятия"""
    try:
        # Парсим дату и время
        datetime_str = f"{date} {start_time}"
        start_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration)

        # Создаем занятие
        lesson = Schedule(
            title=title,
            description=description,
            start_time=start_datetime,
            end_time=end_datetime,
            teacher_id=teacher_id,
            student_id=current_user.id,
            status=ScheduleStatus.PLANNED
        )

        db.add(lesson)
        db.commit()
        db.refresh(lesson)

        # Создаем уведомление
        NotificationManager.create_lesson_reminder_notification(
            db=db,
            user_id=current_user.id,
            lesson_id=lesson.id,
            lesson_title=lesson.title,
            lesson_time=lesson.start_time
        )

        return RedirectResponse(url="/schedule/", status_code=303)

    except ValueError:
        return templates.TemplateResponse(
            "schedule/add_lesson.html",
            {
                "request": request,
                "error": "Неверный формат даты или времени",
                "title": title,
                "description": description,
                "date": date,
                "start_time": start_time,
                "duration": duration
            }
        )


@router.post("/{lesson_id}/cancel")
async def cancel_lesson(
        lesson_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Отмена занятия"""
    lesson = db.query(Schedule).filter(
        Schedule.id == lesson_id,
        Schedule.student_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    lesson.status = ScheduleStatus.CANCELLED
    db.commit()

    return {"message": "Занятие отменено"}


@router.post("/{lesson_id}/complete")
async def complete_lesson(
        lesson_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Отметить занятие как завершенное"""
    lesson = db.query(Schedule).filter(
        Schedule.id == lesson_id,
        Schedule.student_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    lesson.status = ScheduleStatus.COMPLETED
    db.commit()

    return {"message": "Занятие отмечено как завершенное"}


@router.get("/{lesson_id}")
async def get_lesson(
        lesson_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получить информацию о занятии"""
    lesson = db.query(Schedule).filter(
        Schedule.id == lesson_id,
        (Schedule.student_id == current_user.id) | (Schedule.teacher_id == current_user.id)
    ).first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Занятие не найдено")

    return lesson


@router.get("/api/upcoming")
async def get_upcoming_lessons(
        days: int = 7,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """API: Получить предстоящие занятия"""
    now = datetime.now()
    end_date = now + timedelta(days=days)

    lessons = db.query(Schedule).filter(
        Schedule.student_id == current_user.id,
        Schedule.start_time > now,
        Schedule.start_time <= end_date,
        Schedule.status == ScheduleStatus.PLANNED
    ).order_by(Schedule.start_time).all()

    return {"lessons": lessons, "count": len(lessons)}


@router.post("/recurring/add")
async def add_recurring_lesson(
        request: Request,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        day_of_week: int = Form(...),
        start_time: str = Form(...),
        duration: int = Form(60),
        teacher_id: int = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Добавить регулярное занятие"""
    recurring = RecurringSchedule(
        title=title,
        description=description,
        day_of_week=day_of_week,
        start_time=start_time,
        duration_minutes=duration,
        teacher_id=teacher_id,
        student_id=current_user.id,
        is_active=True
    )

    db.add(recurring)
    db.commit()

    return RedirectResponse(url="/schedule/manage", status_code=303)


@router.post("/recurring/{recurring_id}/toggle")
async def toggle_recurring_lesson(
        recurring_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Включить/выключить регулярное занятие"""
    recurring = db.query(RecurringSchedule).filter(
        RecurringSchedule.id == recurring_id,
        RecurringSchedule.student_id == current_user.id
    ).first()

    if not recurring:
        raise HTTPException(status_code=404, detail="Регулярное занятие не найдено")

    recurring.is_active = not recurring.is_active
    db.commit()

    return {"message": "Статус обновлен", "is_active": recurring.is_active}