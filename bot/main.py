import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.database.middleware import DatabaseMiddleware
from bot.handlers import register_all_handlers
from bot.services.notification_service import start_notification_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Основная функция запуска бота
    logger.info("Запуск бота...")
    
    try:
        # Инициализация бота и диспетчера
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Регистрация хендлеров
        register_all_handlers(dp)
        
        # Добавление middleware для работы с сессией
        dp.update.middleware(DatabaseMiddleware())
        
        # Запуск сервиса уведомлений
        await start_notification_service(bot)
        
        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())