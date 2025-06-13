    # bot/ai/generator.py
import re
from bot.config import AI_TOKEN
from openai import AsyncClient

async def generate_response(prompt):
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
    # **жирный текст** -> <b>жирный текст</b>
    response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)         # **жирный**
    response = re.sub(r'\*(.*?)\*', r'<i>\1</i>', response)             # *курсив*
    response = re.sub(r'__(.*?)__', r'<u>\1</u>', response)             # __подчёркнутый__
    response = re.sub(r'~~(.*?)~~', r'<s>\1</s>', response)             # ~~зачёркнутый~~
    return response

