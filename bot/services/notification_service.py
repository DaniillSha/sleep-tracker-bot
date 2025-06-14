import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.db_service import SessionLocal
from bot.database.tables import User
from bot.keyboards.InlineButtons import analyze_kb

logger = logging.getLogger(__name__)

async def check_notifications(bot):
    # Проверяет и отправляет уведомления пользователям
    while True:
        try:
            # Получаем текущее время в московском часовом поясе
            moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))
            logger.info(f"Проверка уведомлений для времени по МСК: {moscow_time.strftime('%H:%M')}")
            
            async with SessionLocal() as session:
                # Получаем всех пользователей с включенными уведомлениями
                query = select(User).where(User.notifications_enabled == True)
                result = await session.execute(query)
                users = result.scalars().all()
                
                for user in users:
                    try:
                        # Вычисляем время пользователя с учетом его часового пояса
                        user_time = moscow_time + timedelta(hours=user.timezone_offset)
                        user_time_str = user_time.strftime("%H:%M")
                        
                        # Если время совпадает с настройками пользователя
                        if user.notification_time == user_time_str:
                            logger.info(f"Отправлено уведомление для {user.telegram_id} в {user_time_str}")
                            await bot.send_message(
                                user.telegram_id,
                                "Доброе утро! 🌅\n\nПора заполнить дневник сна и получить анализ!",
                                reply_markup=analyze_kb
                            )
                            logger.info(f"Успешно отправлено уведомление для {user.telegram_id}")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}")
                
        except Exception as e:
            logger.error(f"Ошибка при проверке уведомлений: {e}")
        
        # Ждем 1 минуту перед следующей проверкой
        await asyncio.sleep(60)

async def start_notification_service(bot):
    # Запускает сервис уведомлений
    logger.info("Запуск сервиса уведомлений...")
    asyncio.create_task(check_notifications(bot))
    logger.info("Сервис уведомлений успешно запущен") 