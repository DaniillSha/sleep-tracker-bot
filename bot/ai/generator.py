    # bot/ai/generator.py
import logging
import re

from openai import AsyncClient

from bot.config import AI_TOKEN

logger = logging.getLogger(__name__)

async def generate_response(prompt):
    # Генерирует ответ от AI модели и форматирует его для Telegram
    try:
        client = AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            api_key=AI_TOKEN,
        )

        # Отправка запроса к AI модели
        completion = await client.chat.completions.create(
            extra_body={},
            model="qwen/qwen3-30b-a3b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Получаем ответ от модели
        response = completion.choices[0].message.content

        # Форматирование markdown в HTML-теги для Telegram
        response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)  # **жирный**
        response = re.sub(r'\*(.*?)\*', r'<i>\1</i>', response)      # *курсив*
        response = re.sub(r'__(.*?)__', r'<u>\1</u>', response)      # __подчёркнутый__
        response = re.sub(r'~~(.*?)~~', r'<s>\1</s>', response)      # ~~зачёркнутый~~
        
        return response
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {e}")
        raise

