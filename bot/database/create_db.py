import asyncio
from bot.database.connect import engine
from bot.database.tables import Base

async def init_db():
    async with engine.begin() as conn:
        print("Создание таблиц, если их ещё нет...")
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())