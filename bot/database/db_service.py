import logging
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.connect import SessionLocal
from bot.database.tables import SleepEntry, User

logger = logging.getLogger(__name__)

async def check_user_exists(telegram_id: int) -> bool:
    # Проверяет существование пользователя
    async with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

async def get_or_create_user(telegram_id: int) -> User:
    # Получает существующего пользователя или создает нового
    async with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Создан новый пользователь с telegram_id: {telegram_id}")
        
        return user

async def save_sleep_entry(telegram_id: int, data: dict) -> SleepEntry:
    # Сохраняет запись о сне в базу данных
    async with SessionLocal() as session:
        try:
            user = await get_or_create_user(telegram_id)
            
            # Преобразуем время из строки в объект time
            sleep_time_str = data.get('sleep_time', '00:00')
            sleep_time = datetime.strptime(sleep_time_str, '%H:%M').time()
            
            # Преобразуем имена полей в соответствии с моделью
            entry_data = {
                'telegram_id': telegram_id,
                'date': datetime.date.today(),
                'feeling_score': data.get('feeling'),
                'sleep_hours': data.get('sleep_hours'),
                'stress_score': data.get('stress_level'),
                'food_type': data.get('food_before_sleep'),
                'sleep_time': sleep_time,
                'tired': data.get('tired'),
                'woke_up': data.get('woke_up'),
                'had_dreams': data.get('had_dreams'),
                'dream_text': data.get('dream_content'),
                'extra_notes': data.get('additional_info')
            }
            
            entry = SleepEntry(**entry_data)
            session.add(entry)
            await session.commit()
            logger.info(f"Запись о сне сохранена для пользователя {telegram_id}")
            return entry
        except Exception as e:
            logger.error(f"Ошибка при сохранении записи о сне: {e}")
            raise

async def get_sleep_entries_for_month(telegram_id: int) -> list[SleepEntry]:
    # Получает записи о сне за последний месяц
    async with SessionLocal() as session:
        try:
            stmt = select(SleepEntry)\
                .join(User)\
                .where(User.telegram_id == telegram_id)\
                .order_by(SleepEntry.id.desc())\
                .limit(30)
            result = await session.execute(stmt)
            entries = result.scalars().all()
            logger.info(f"Получено {len(entries)} записей о сне для пользователя {telegram_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка при получении записей о сне: {e}")
            raise

async def get_user_notifications(telegram_id: int) -> User:
    # Получает настройки уведомлений пользователя
    async with SessionLocal() as session:
        try:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"Получены настройки уведомлений для пользователя {telegram_id}")
            return user
        except Exception as e:
            logger.error(f"Ошибка при получении настроек уведомлений: {e}")
            raise

async def enable_notifications(telegram_id: int, time: str):
    # Включает уведомления для пользователя
    async with SessionLocal() as session:
        try:
            stmt = update(User)\
                .where(User.telegram_id == telegram_id)\
                .values(notifications_enabled=True, notification_time=time)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Включены уведомления для пользователя {telegram_id} в {time}")
        except Exception as e:
            logger.error(f"Ошибка при включении уведомлений: {e}")
            raise

async def disable_notifications(telegram_id: int):
    # Отключает уведомления для пользователя
    async with SessionLocal() as session:
        try:
            stmt = update(User)\
                .where(User.telegram_id == telegram_id)\
                .values(notifications_enabled=False, notification_time=None)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Отключены уведомления для пользователя {telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при отключении уведомлений: {e}")
            raise

async def update_user_timezone(telegram_id: int, timezone_offset: int) -> None:
    # Обновляет часовой пояс пользователя
    async with SessionLocal() as session:
        try:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user:
                user.timezone_offset = timezone_offset
                await session.commit()
                logger.info(f"Обновлен часовой пояс для пользователя {telegram_id}: {timezone_offset}")
        except Exception as e:
            logger.error(f"Ошибка при обновлении часового пояса: {e}")
            raise