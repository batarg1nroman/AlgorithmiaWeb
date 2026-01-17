// JavaScript для AI Assistant

class AIAssistant {
    constructor() {
        this.messages = [];
        this.isOpen = false;
        this.userData = {};
        this.init();
    }

    init() {
        // Кнопка открытия AI Assistant
        const aiBtn = document.getElementById('ai-assistant-btn');
        const modal = document.getElementById('ai-assistant-modal');
        const closeBtn = modal.querySelector('.close-btn');
        const sendBtn = document.getElementById('ai-send-btn');
        const fileInput = document.getElementById('ai-file-upload');
        const chatInput = document.getElementById('ai-chat-input');
        const messagesContainer = document.getElementById('ai-chat-messages');

        // Открытие/закрытие модального окна
        aiBtn.addEventListener('click', () => this.openModal());
        closeBtn.addEventListener('click', () => this.closeModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });

        // Отправка сообщения
        sendBtn.addEventListener('click', () => this.sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Загрузка файла
        fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        // Загрузка истории чата из localStorage
        this.loadHistory();
    }

    openModal() {
        const modal = document.getElementById('ai-assistant-modal');
        modal.style.display = 'flex';
        this.isOpen = true;

        // Фокус на поле ввода
        setTimeout(() => {
            document.getElementById('ai-chat-input').focus();
        }, 100);
    }

    closeModal() {
        const modal = document.getElementById('ai-assistant-modal');
        modal.style.display = 'none';
        this.isOpen = false;

        // Сохраняем историю
        this.saveHistory();
    }

    async sendMessage() {
        const input = document.getElementById('ai-chat-input');
        const fileInput = document.getElementById('ai-file-upload');
        const message = input.value.trim();
        const file = fileInput.files[0];

        if (!message && !file) return;

        // Добавляем сообщение пользователя
        this.addMessage('user', message, file);

        // Очищаем поля
        input.value = '';
        fileInput.value = '';

        // Показываем индикатор загрузки
        this.showTypingIndicator();

        try {
            // Создаем FormData
            const formData = new FormData();
            if (file) formData.append('photo', file);
            if (message) formData.append('question', message);

            // Добавляем данные пользователя
            const userData = this.getUserData();
            formData.append('user', JSON.stringify(userData));

            // Отправляем запрос
            const response = await fetch('/ai/ask_stream', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Обрабатываем потоковый ответ
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = this.addMessage('assistant', '');

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                assistantMessage.textContent += chunk;
                this.scrollToBottom();
            }

            // Удаляем индикатор загрузки
            this.removeTypingIndicator();

        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addMessage('assistant', 'Произошла ошибка. Пожалуйста, попробуйте еще раз.');
        }
    }

    addMessage(sender, text, file = null) {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${sender}`;

        let content = text;
        if (file) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    messageDiv.innerHTML += `<img src="${e.target.result}" style="max-width: 100%; max-height: 300px; border-radius: 8px; margin-bottom: 10px;">`;
                };
                reader.readAsDataURL(file);
            } else {
                content = `📎 Файл: ${file.name}\n${text}`;
            }
        }

        const textNode = document.createElement('div');
        textNode.textContent = content;
        messageDiv.appendChild(textNode);

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        // Сохраняем в историю
        this.messages.push({
            sender,
            text: content,
            timestamp: new Date().toISOString()
        });

        return textNode;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ai-message assistant typing';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            // Можно добавить предпросмотр
            console.log('File selected:', file.name);
        }
    }

    getUserData() {
        // Получаем данные пользователя из cookie или localStorage
        // В реальном приложении здесь будет логика получения данных пользователя
        return {
            id: localStorage.getItem('user_id') || 'web_user',
            email: localStorage.getItem('user_email') || ''
        };
    }

    saveHistory() {
        // Сохраняем историю в localStorage
        localStorage.setItem('ai_chat_history', JSON.stringify(this.messages.slice(-50))); // Сохраняем последние 50 сообщений
    }

    loadHistory() {
        // Загружаем историю из localStorage
        const savedHistory = localStorage.getItem('ai_chat_history');
        if (savedHistory) {
            this.messages = JSON.parse(savedHistory);
            // Восстанавливаем сообщения в UI
            this.messages.forEach(msg => {
                this.addMessage(msg.sender, msg.text);
            });
        }
    }
}

// Инициализация AI Assistant при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.aiAssistant = new AIAssistant();
});