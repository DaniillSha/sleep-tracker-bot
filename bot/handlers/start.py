from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import main_menu_kb, analyze_kb, timezone_kb
from bot.database.db_service import check_user_exists, get_or_create_user, update_user_timezone
from bot.utils import generate_test_data, clear_test_data
from bot.states import MainMenu, UserSetup
import random

MOTIVATION_QUOTES = [
    "Каждое утро — новый шанс сделать себя сильнее 💪",
    "Хороший сон — это инвестиция в продуктивность!",
    "Ты уже на пути к лучшему себе. Продолжай!",
    "Твоё тело скажет тебе спасибо за заботу ❤️",
    "Маленькие привычки создают большие перемены 🌱",
]

router = Router()

@router.message(F.text == "/start")
async def show_main_menu(message: Message, state: FSMContext, bot: Bot):
    first_name = message.from_user.first_name
    quote = random.choice(MOTIVATION_QUOTES)
    
    # Устанавливаем состояние главного меню
    await state.set_state(MainMenu.menu)
    
    # Проверяем, существует ли пользователь
    user_exists = await check_user_exists(message.from_user.id)
    
    if not user_exists:
        # Для новых пользователей показываем приветствие и запрашиваем часовой пояс
        text = f"""
<b>Привет, {first_name}!</b> 👋

Я бот-ассистент для анализа твоего сна. Я помогу тебе отслеживать качество сна и давать рекомендации по его улучшению.

Для корректной работы уведомлений, пожалуйста, выбери свой часовой пояс относительно Москвы:

✨ <i>{quote}</i>
"""
        await bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=timezone_kb())
        await state.set_state(UserSetup.waiting_for_timezone)
    else:
        # Для существующих пользователей показываем полное меню
        text = f"""
<b>С возвращением, {first_name}!</b> 👋

Добро пожаловать в ассистент сна — твой инструмент для анализа и улучшения сна 🛌

<b>🧠 Анализ сна</b>  
Пройди опрос — получишь краткий анализ и полезные рекомендации.

<b>⏰ Включить уведомления</b>  
Бот напомнит утром пройти опрос, чтобы ты не забыл.

<b>📅 История сна</b>  
Посмотри, как ты спал в конкретный день.

<b>📊 Статистика сна</b>  
Узнай, что влияет на твой сон и как его улучшить.

✨ <i>{quote}</i>
"""
        await bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_menu_kb)

@router.callback_query(UserSetup.waiting_for_timezone, F.data.startswith("tz_"))
async def process_timezone(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обрабатывает выбор часового пояса"""
    await callback.answer()
    
    # Получаем смещение из callback data (например, "tz_-3" -> -3)
    offset = int(callback.data.split("_")[1])
    
    # Создаем пользователя и сохраняем часовой пояс
    await get_or_create_user(callback.from_user.id)
    await update_user_timezone(callback.from_user.id, offset)
    
    # Показываем основное меню
    text = f"""
<b>Отлично!</b> 👌

Теперь давай начнем с первой записи о твоем сне? Это поможет мне лучше понять твой режим и давать более точные рекомендации.

✨ <i>{random.choice(MOTIVATION_QUOTES)}</i>
"""
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=analyze_kb)
    await state.set_state(MainMenu.menu)

@router.callback_query(F.data == "show_main_menu")
async def handle_show_main_menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик кнопки возврата в главное меню"""
    await callback.answer()
    
    # Создаем новое сообщение с правильным отправителем
    message = Message(
        message_id=callback.message.message_id,
        date=callback.message.date,
        chat=callback.message.chat,
        from_user=callback.from_user,
        text="/start"
    )
    
    await show_main_menu(message, state, bot)

@router.message(F.text == "/generate_test_data")
async def cmd_generate_test_data(message: Message):
    await message.answer("Генерирую тестовые данные...")
    await generate_test_data(message.from_user.id)
    await message.answer("✅ Тестовые данные успешно сгенерированы!")

@router.message(F.text == "/clear_test_data")
async def cmd_clear_test_data(message: Message):
    await message.answer("Удаляю тестовые данные...")
    await clear_test_data(message.from_user.id)
    await message.answer("✅ Тестовые данные успешно удалены!")