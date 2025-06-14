import logging
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from .connect import SessionLocal

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    # Middleware для добавления сессии базы данных в контекст обработчика
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            async with SessionLocal() as session:
                data["session"] = session
                return await handler(event, data)
        except Exception as e:
            logger.error(f"Ошибка в DatabaseMiddleware: {e}")
            raise 