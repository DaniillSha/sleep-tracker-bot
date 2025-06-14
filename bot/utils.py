import logging
import random
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from bot.database.connect import SessionLocal
from bot.database.tables import SleepEntry

logger = logging.getLogger(__name__)

async def generate_test_data(telegram_id: int, days: int = 30):
    """
    Генерирует тестовые данные о сне за последние N дней.
    
    Args:
        telegram_id: ID пользователя в Telegram
        days: Количество дней для генерации данных
    """
    try:
        async with SessionLocal() as session:
            # Генерируем данные за последние N дней
            for i in range(days):
                date = datetime.now().date() - timedelta(days=i)
                
                # Генерируем случайные данные
                entry = SleepEntry(
                    telegram_id=telegram_id,
                    date=date,
                    feeling_score=random.randint(1, 10),
                    had_dreams=random.choice([True, False]),
                    dream_text=random.choice([
                        "Приснился полет над городом",
                        "Снился пляж и океан",
                        "Странный сон про работу",
                        "Приснились друзья",
                        "Снился старый дом",
                        None
                    ]),
                    woke_up=random.choice([True, False]),
                    tired=random.choice([True, False]),
                    sleep_hours=round(random.uniform(4.0, 10.0), 1),
                    stress_score=random.randint(1, 10),
                    food_type=random.choice(["тяжёлая", "лёгкая", "не ел"]),
                    sleep_time=datetime.strptime(f"{random.randint(21, 23)}:{random.randint(0, 59)}", "%H:%M").time(),
                    extra_notes=random.choice([
                        "Спал хорошо",
                        "Было жарко",
                        "Шумно было",
                        "Спал в неудобной позе",
                        "Проснулся от шума",
                        None
                    ])
                )
                session.add(entry)
            
            await session.commit()
            logger.info(f"Сгенерированы тестовые данные для пользователя {telegram_id} за {days} дней")
    except Exception as e:
        logger.error(f"Ошибка при генерации тестовых данных: {e}")
        raise

async def clear_test_data(telegram_id: int, days: int = 30):
    """
    Удаляет записи о сне за последние N дней.
    
    Args:
        telegram_id: ID пользователя в Telegram
        days: Количество дней для очистки
    """
    try:
        async with SessionLocal() as session:
            # Вычисляем дату, с которой нужно удалить записи
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            # Удаляем записи
            stmt = delete(SleepEntry).where(
                SleepEntry.telegram_id == telegram_id,
                SleepEntry.date >= cutoff_date
            )
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Удалены тестовые данные для пользователя {telegram_id} за {days} дней")
    except Exception as e:
        logger.error(f"Ошибка при удалении тестовых данных: {e}")
        raise 