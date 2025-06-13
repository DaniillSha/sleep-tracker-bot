# Sleep Tracker Bot

Telegram бот для отслеживания качества сна и получения персонализированных рекомендаций.
Выполнено в рамках проекта ПиОА 2025

## Возможности

- 📝 Ежедневный опрос о качестве сна
- 📊 Анализ статистики сна за последние 30 дней
- 🤖 AI-рекомендации для улучшения сна
- ⏰ Настраиваемые уведомления
- 🌍 Поддержка разных часовых поясов
- 📈 Визуализация данных о сне

## Технологии

- Python 3.9+
- PostgreSQL
- Redis
- Docker
- OpenAI GPT
- Pandas для анализа данных
- SQLAlchemy для работы с БД
- aiogram для Telegram бота

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/DaniillSha/sleep-tracker-bot.git
cd sleep-tracker-bot
```

2. Создайте файл `.env` с необходимыми переменными окружения:
```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=sleep_tracker
DB_HOST=db
DB_PORT=5432
```

3. Запустите с помощью Docker Compose:
```bash
docker compose up -d
```

## Структура проекта

```
sleep-tracker-bot/
├── bot/
│   ├── ai/              # AI и аналитика
│   ├── database/        # Модели и миграции БД
│   ├── handlers/        # Обработчики команд
│   ├── keyboards/       # Клавиатуры
│   ├── middlewares/     # Промежуточные обработчики
│   └── services/        # Бизнес-логика
├── docker/             # Docker конфигурации
├── migrations/         # Миграции БД
└── docker-compose.yml  # Docker Compose конфигурация
```

## Использование

1. Найдите бота в Telegram по имени @your_bot_name
2. Отправьте команду `/start` для начала работы
3. Следуйте инструкциям бота для настройки и использования

## Лицензия

MIT 
