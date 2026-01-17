# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user
)
from app.utils.validators import validate_email, validate_password
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Конфигурация
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    # Находим пользователя
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Неверное имя пользователя или пароль"
            }
        )

    if not user.is_active:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Аккаунт деактивирован"
            }
        )

    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    # Устанавливаем куки или сессию (здесь простой редирект)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        email: str = Form(...),
        username: str = Form(...),
        full_name: Optional[str] = Form(None),
        password: str = Form(...),
        password_confirm: str = Form(...),
        db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Валидация данных
    email_valid, email_error = validate_email(email)
    if not email_valid:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": email_error,
                "email": email,
                "username": username,
                "full_name": full_name
            }
        )

    password_valid, password_error = validate_password(password)
    if not password_valid:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": password_error,
                "email": email,
                "username": username,
                "full_name": full_name
            }
        )

    if password != password_confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пароли не совпадают",
                "email": email,
                "username": username,
                "full_name": full_name
            }
        )

    # Проверка существования пользователя
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Пользователь с таким email или username уже существует",
                "email": email,
                "username": username,
                "full_name": full_name
            }
        )

    # Создание пользователя
    try:
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False  # Можно добавить верификацию по email
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Автоматический логин после регистрации
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

        return response

    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "error": "Произошла ошибка при создании пользователя",
                "email": email,
                "username": username,
                "full_name": full_name
            }
        )


@router.get("/logout")
async def logout():
    """Выход из системы"""
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie(key="access_token")
    return response


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
        request: Request,
        current_user: User = Depends(get_current_user)
):
    """Страница профиля"""
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user
        }
    )


@router.post("/profile/update")
async def update_profile(
        request: Request,
        full_name: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обновление профиля"""
    if email and email != current_user.email:
        # Проверка email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return templates.TemplateResponse(
                "profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": email_error
                }
            )

        # Проверка уникальности email
        existing_user = db.query(User).filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_user:
            return templates.TemplateResponse(
                "profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": "Этот email уже используется другим пользователем"
                }
            )

        current_user.email = email

    if full_name:
        current_user.full_name = full_name

    db.commit()

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user,
            "success": "Профиль успешно обновлен"
        }
    )


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }


@router.get("/check-auth")
async def check_auth(current_user: User = Depends(get_current_user)):
    """Проверка аутентификации"""
    return {"authenticated": True, "username": current_user.username}