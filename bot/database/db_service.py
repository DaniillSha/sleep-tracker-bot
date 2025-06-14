from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.connect import SessionLocal
from bot.database.tables import User, SleepEntry
import logging

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
            logger.info(f"Created new user with telegram_id: {telegram_id}")
        
        return user


async def save_sleep_entry(telegram_id: int, data: dict) -> SleepEntry:
    # Открываем сессию с БД
    async with SessionLocal() as session:
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
        return entry

    #bot/database/db_service.py
async def get_sleep_entries_for_month(telegram_id: int) -> list[SleepEntry]:
    # Получает записи о сне за последний месяц
    async with SessionLocal() as session:
        stmt = select(SleepEntry)\
            .join(User)\
            .where(User.telegram_id == telegram_id)\
            .order_by(SleepEntry.id.desc())\
            .limit(30)
        result = await session.execute(stmt)
        return result.scalars().all()

# Функции для работы с уведомлениями
async def get_user_notifications(telegram_id: int) -> User:
    # Получает настройки уведомлений пользователя
    async with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def enable_notifications(telegram_id: int, time: str):
    # Включает уведомления для пользователя
    async with SessionLocal() as session:
        stmt = update(User)\
            .where(User.telegram_id == telegram_id)\
            .values(notifications_enabled=True, notification_time=time)
        await session.execute(stmt)
        await session.commit()
        logger.info(f"Enabled notifications for user {telegram_id} at {time}")

async def disable_notifications(telegram_id: int):
    # Отключает уведомления для пользователя
    async with SessionLocal() as session:
        stmt = update(User)\
            .where(User.telegram_id == telegram_id)\
            .values(notifications_enabled=False, notification_time=None)
        await session.execute(stmt)
        await session.commit()
        logger.info(f"Disabled notifications for user {telegram_id}")

async def update_user_timezone(telegram_id: int, timezone_offset: int) -> None:
    # Обновляет часовой пояс пользователя
    async with SessionLocal() as session:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            user.timezone_offset = timezone_offset
            await session.commit()