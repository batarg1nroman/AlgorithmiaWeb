import os

structure = {
    "tutor_website/app/__init__.py": "",
    "tutor_website/app/main.py": "",
    "tutor_website/app/config.py": "",
    "tutor_website/app/database.py": "",
    "tutor_website/app/models/__init__.py": "",
    "tutor_website/app/models/user.py": "",
    "tutor_website/app/models/schedule.py": "",
    "tutor_website/app/models/homework.py": "",
    "tutor_website/app/models/notification.py": "",
    "tutor_website/app/routes/__init__.py": "",
    "tutor_website/app/routes/auth.py": "",
    "tutor_website/app/routes/schedule.py": "",
    "tutor_website/app/routes/homework.py": "",
    "tutor_website/app/routes/knowledge_base.py": "",
    "tutor_website/app/routes/notifications.py": "",
    "tutor_website/app/routes/ai_assistant.py": "",
    "tutor_website/app/templates/base.html": "",
    "tutor_website/app/templates/index.html": "",
    "tutor_website/app/templates/profile.html": "",
    "tutor_website/app/templates/auth/login.html": "",
    "tutor_website/app/templates/auth/register.html": "",
    "tutor_website/app/templates/schedule/schedule.html": "",
    "tutor_website/app/templates/schedule/manage_schedule.html": "",
    "tutor_website/app/templates/schedule/add_lesson.html": "",
    "tutor_website/app/templates/homework/homework.html": "",
    "tutor_website/app/templates/homework/submit_homework.html": "",
    "tutor_website/app/templates/homework/view_homework.html": "",
    "tutor_website/app/templates/knowledge_base/math.html": "",
    "tutor_website/app/templates/knowledge_base/topics.html": "",
    "tutor_website/app/static/css/style.css": "",
    "tutor_website/app/static/js/main.js": "",
    "tutor_website/app/static/js/ai_assistant.js": "",
    "tutor_website/app/utils/__init__.py": "",
    "tutor_website/app/utils/notifications.py": "",
    "tutor_website/app/utils/validators.py": "",
    "uploads/homework_files/.gitkeep": "",
    "uploads/chat_histories/.gitkeep": "",
    "tutor_website/requirements.txt": "",
    "tutor_website/.env": "",
    "tutor_website/.gitignore": "",
    "tutor_website/run.py": "",
}

for path, content in structure.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Структура проекта создана!")