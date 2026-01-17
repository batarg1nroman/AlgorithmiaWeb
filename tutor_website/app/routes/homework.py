# app/routes/homework.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import shutil

from app.database import get_db
from app.models.user import User
from app.models.homework import Homework, HomeworkStatus
from app.models.schedule import Schedule
from app.utils.auth import get_current_user
from app.utils.notifications import NotificationManager

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Папка для загрузки файлов
UPLOAD_DIR = "uploads/homework_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_class=HTMLResponse)
async def homework_page(
        request: Request,
        status: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Страница домашних заданий"""
    query = db.query(Homework).filter(Homework.student_id == current_user.id)

    if status:
        try:
            status_enum = HomeworkStatus(status)
            query = query.filter(Homework.status == status_enum)
        except ValueError:
            pass

    # Сортируем по сроку сдачи
    homeworks = query.order_by(Homework.due_date).all()

    # Статистика
    stats = {
        "total": db.query(Homework).filter(Homework.student_id == current_user.id).count(),
        "assigned": db.query(Homework).filter(
            Homework.student_id == current_user.id,
            Homework.status == HomeworkStatus.ASSIGNED
        ).count(),
        "submitted": db.query(Homework).filter(
            Homework.student_id == current_user.id,
            Homework.status == HomeworkStatus.SUBMITTED
        ).count(),
        "reviewed": db.query(Homework).filter(
            Homework.student_id == current_user.id,
            Homework.status == HomeworkStatus.REVIEWED
        ).count(),
        "late": db.query(Homework).filter(
            Homework.student_id == current_user.id,
            Homework.status == HomeworkStatus.LATE
        ).count(),
    }

    return templates.TemplateResponse(
        "homework/homework.html",
        {
            "request": request,
            "homeworks": homeworks,
            "status": status,
            "stats": stats,
            "status_options": [s.value for s in HomeworkStatus]
        }
    )


@router.get("/view/{homework_id}", response_class=HTMLResponse)
async def view_homework(
        homework_id: int,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Просмотр домашнего задания"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")

    return templates.TemplateResponse(
        "homework/view_homework.html",
        {
            "request": request,
            "homework": homework
        }
    )


@router.get("/submit/{homework_id}", response_class=HTMLResponse)
async def submit_homework_page(
        homework_id: int,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Страница отправки домашнего задания"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")

    # Проверяем, можно ли еще отправить
    if homework.status in [HomeworkStatus.SUBMITTED, HomeworkStatus.REVIEWED]:
        return templates.TemplateResponse(
            "homework/view_homework.html",
            {
                "request": request,
                "homework": homework,
                "error": "Это задание уже отправлено или проверено"
            }
        )

    # Проверяем дедлайн
    if homework.due_date < datetime.now():
        return templates.TemplateResponse(
            "homework/view_homework.html",
            {
                "request": request,
                "homework": homework,
                "error": "Срок сдачи истек"
            }
        )

    return templates.TemplateResponse(
        "homework/submit_homework.html",
        {
            "request": request,
            "homework": homework
        }
    )


@router.post("/submit/{homework_id}")
async def submit_homework(
        homework_id: int,
        request: Request,
        comment: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Отправить домашнее задание"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")

    # Сохраняем файл
    file_path = None
    if file and file.filename:
        # Создаем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{homework_id}_{current_user.id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        homework.submission_path = file_path

    # Обновляем статус
    homework.status = HomeworkStatus.SUBMITTED
    homework.submitted_date = datetime.now()

    if comment:
        # Можно добавить поле для комментария студента
        pass

    db.commit()

    # Отправляем уведомление преподавателю
    NotificationManager.create_notification(
        db=db,
        user_id=homework.teacher_id,
        title="Домашнее задание отправлено",
        message=f"Студент {current_user.username} отправил домашнее задание: {homework.title}",
        related_entity_type="homework",
        related_entity_id=homework.id,
        action_url=f"/homework/review/{homework.id}"
    )

    return RedirectResponse(url=f"/homework/view/{homework_id}", status_code=303)


@router.get("/download/{homework_id}")
async def download_homework_file(
        homework_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Скачать файл домашнего задания"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework or not homework.attachment_path:
        raise HTTPException(status_code=404, detail="Файл не найден")

    if not os.path.exists(homework.attachment_path):
        raise HTTPException(status_code=404, detail="Файл не существует")

    return FileResponse(
        homework.attachment_path,
        filename=os.path.basename(homework.attachment_path)
    )


@router.get("/download-submission/{homework_id}")
async def download_submission_file(
        homework_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Скачать отправленный файл"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework or not homework.submission_path:
        raise HTTPException(status_code=404, detail="Файл не найден")

    if not os.path.exists(homework.submission_path):
        raise HTTPException(status_code=404, detail="Файл не существует")

    return FileResponse(
        homework.submission_path,
        filename=os.path.basename(homework.submission_path)
    )


@router.get("/api/upcoming")
async def get_upcoming_homework(
        days: int = 7,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """API: Получить предстоящие домашние задания"""
    now = datetime.now()
    end_date = now + timedelta(days=days)

    homeworks = db.query(Homework).filter(
        Homework.student_id == current_user.id,
        Homework.due_date > now,
        Homework.due_date <= end_date,
        Homework.status.in_([HomeworkStatus.ASSIGNED, HomeworkStatus.IN_PROGRESS])
    ).order_by(Homework.due_date).all()

    return {"homeworks": homeworks, "count": len(homeworks)}


@router.get("/api/late")
async def get_late_homework(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """API: Получить просроченные задания"""
    now = datetime.now()

    homeworks = db.query(Homework).filter(
        Homework.student_id == current_user.id,
        Homework.due_date < now,
        Homework.status.in_([HomeworkStatus.ASSIGNED, HomeworkStatus.IN_PROGRESS])
    ).order_by(Homework.due_date).all()

    # Обновляем статус на LATE
    for hw in homeworks:
        if hw.status != HomeworkStatus.LATE:
            hw.status = HomeworkStatus.LATE
    db.commit()

    return {"homeworks": homeworks, "count": len(homeworks)}


@router.post("/{homework_id}/start")
async def start_homework(
        homework_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Начать работу над заданием"""
    homework = db.query(Homework).filter(
        Homework.id == homework_id,
        Homework.student_id == current_user.id
    ).first()

    if not homework:
        raise HTTPException(status_code=404, detail="Домашнее задание не найдено")

    if homework.status == HomeworkStatus.ASSIGNED:
        homework.status = HomeworkStatus.IN_PROGRESS
        db.commit()

    return {"message": "Работа над заданием начата", "status": homework.status.value}