from typing import AsyncGenerator, Any, Awaitable, Callable, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from .connect import SessionLocal

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with SessionLocal() as session:
            data["session"] = session
            return await handler(event, data) 