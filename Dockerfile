FROM python:3.11-slim

# Рабочая директория — корень проекта
WORKDIR /app

# Копируем файлы конфигурации и миграций
COPY requirements.txt .
COPY .env .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем модуль бота (импорт будет from bot.config и т.п.)
CMD ["python", "-m", "bot.main"]