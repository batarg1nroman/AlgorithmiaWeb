// Основные функции JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация табов если есть
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            openTab(event, tabId);
        });
    });

    // Инициализация календаря если есть
    if (document.querySelector('.calendar')) {
        initCalendar();
    }

    // Обработка форм с подтверждением
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Отображение уведомлений
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    });
});

// Функция для переключения табов
function openTab(evt, tabId) {
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    document.getElementById(tabId).classList.add('active');
    if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add('active');
    }
}

// Функция для инициализации календаря
function initCalendar() {
    const calendarEl = document.querySelector('.calendar');
    if (!calendarEl) return;

    // Простая реализация календаря
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();

    // Можно интегрировать с библиотекой FullCalendar
    // Для простоты сделаем базовую версию
    const monthNames = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ];

    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const firstDay = new Date(year, month, 1).getDay();

    let calendarHTML = `
        <div class="calendar-header">
            <button class="prev-month"><i class="fas fa-chevron-left"></i></button>
            <h3>${monthNames[month]} ${year}</h3>
            <button class="next-month"><i class="fas fa-chevron-right"></i></button>
        </div>
        <div class="calendar-grid">
            <div class="day-name">Пн</div>
            <div class="day-name">Вт</div>
            <div class="day-name">Ср</div>
            <div class="day-name">Чт</div>
            <div class="day-name">Пт</div>
            <div class="day-name">Сб</div>
            <div class="day-name">Вс</div>
    `;

    // Пустые клетки для первого дня
    for (let i = 0; i < (firstDay === 0 ? 6 : firstDay - 1); i++) {
        calendarHTML += '<div class="day empty"></div>';
    }

    // Дни месяца
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        calendarHTML += `
            <div class="day ${isToday ? 'today' : ''}" data-date="${date.toISOString().split('T')[0]}">
                ${day}
            </div>
        `;
    }

    calendarHTML += '</div>';
    calendarEl.innerHTML = calendarHTML;

    // Обработчики для переключения месяцев
    calendarEl.querySelector('.prev-month').addEventListener('click', function() {
        // Логика переключения на предыдущий месяц
    });

    calendarEl.querySelector('.next-month').addEventListener('click', function() {
        // Логика переключения на следующий месяц
    });
}

// Функция для отображения уведомления
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Функция для загрузки файлов
function handleFileUpload(input, previewId) {
    const file = input.files[0];
    if (!file) return;

    const preview = document.getElementById(previewId);
    if (preview) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `<p>Файл: ${file.name}</p>`;
        }
    }
}

// Функция для форматирования даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}