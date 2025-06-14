import asyncio
import logging

from bot.database.connect import engine
from bot.database.tables import Base

logger = logging.getLogger(__name__)

async def init_db():
    # Создает таблицы в базе данных, если они еще не существуют
    try:
        async with engine.begin() as conn:
            logger.info("Создание таблиц в базе данных...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Таблицы успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())