# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationStatus
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def notifications_page(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Страница уведомлений"""
    # Получаем уведомления пользователя
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    # Получаем количество непрочитанных
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    ).count()

    return HTMLResponse(f"""
    <html>
        <head>
            <title>Уведомления</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .notification {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 5px; }}
                .unread {{ background-color: #f0f8ff; border-left: 4px solid #007bff; }}
                .read {{ background-color: #f9f9f9; }}
                .title {{ font-weight: bold; margin-bottom: 5px; }}
                .time {{ color: #666; font-size: 0.9em; }}
                .actions {{ margin-top: 10px; }}
                .badge {{ background-color: #007bff; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <h1>Уведомления <span class="badge">{unread_count} непрочитанных</span></h1>

            <div class="actions">
                <button onclick="markAllAsRead()">Отметить все как прочитанные</button>
            </div>

            <div id="notifications">
                {"".join([
        f'''
                    <div class="notification {'unread' if n.status == NotificationStatus.UNREAD else 'read'}" id="notification-{n.id}">
                        <div class="title">{n.title}</div>
                        <div>{n.message}</div>
                        <div class="time">{n.created_at.strftime('%d.%m.%Y %H:%M')}</div>
                        <div class="actions">
                            {f'<button onclick="markAsRead({n.id})">Отметить как прочитанное</button>' if n.status == NotificationStatus.UNREAD else ''}
                            <button onclick="deleteNotification({n.id})">Удалить</button>
                        </div>
                    </div>
                    '''
        for n in notifications
    ])}
            </div>

            <script>
                async function markAsRead(notificationId) {{
                    const response = await fetch(`/notifications/${{notificationId}}/read`, {{ method: 'POST' }});
                    if (response.ok) {{
                        document.getElementById(`notification-${{notificationId}}`).classList.remove('unread');
                        document.getElementById(`notification-${{notificationId}}`).classList.add('read');
                        updateUnreadCount();
                    }}
                }}

                async function markAllAsRead() {{
                    const response = await fetch('/notifications/read-all', {{ method: 'POST' }});
                    if (response.ok) {{
                        document.querySelectorAll('.notification.unread').forEach(el => {{
                            el.classList.remove('unread');
                            el.classList.add('read');
                        }});
                        updateUnreadCount();
                    }}
                }}

                async function deleteNotification(notificationId) {{
                    const response = await fetch(`/notifications/${{notificationId}}`, {{ method: 'DELETE' }});
                    if (response.ok) {{
                        document.getElementById(`notification-${{notificationId}}`).remove();
                    }}
                }}

                function updateUnreadCount() {{
                    const count = document.querySelectorAll('.notification.unread').length;
                    document.querySelector('.badge').textContent = count + ' непрочитанных';
                }}
            </script>
        </body>
    </html>
    """)


@router.get("/api/list")
async def get_notifications_api(
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """API: Получить уведомления"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.status == NotificationStatus.UNREAD)

    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    total = query.count()

    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.notification_type.value if n.notification_type else None,
                "status": n.status.value,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "action_url": n.action_url
            }
            for n in notifications
        ],
        "total": total,
        "has_more": total > offset + len(notifications)
    }


@router.get("/api/unread-count")
async def get_unread_count_api(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """API: Получить количество непрочитанных уведомлений"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == NotificationStatus.UNREAD
    ).count()

    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification: