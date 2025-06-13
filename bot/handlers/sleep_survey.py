from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.keyboards.InlineButtons import scale_1_to_10_kb, yes_no_kb, food_kb, scale_1_to_5_kb, back_to_menu
from bot.ai.generator import generate_response
from bot.states import SleepSurvey
from bot.ai.prompts import get_sleep_analysis_prompt
from bot.database.db_service import save_sleep_entry

router = Router()

@router.callback_query(F.data == "sleep_analysis")
async def start_sleep_survey(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Как вы себя чувствуете сейчас? (оцените от 1 до 10)", reply_markup=scale_1_to_10_kb())
    await state.set_state(SleepSurvey.feeling)
    await callback.answer()

@router.callback_query(SleepSurvey.feeling, F.data.startswith("scale_"))
async def process_feeling(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    sleep_score = int(callback.data.split("_")[1])
    await state.update_data(feeling=sleep_score)
    # next вопрос
    await callback.message.edit_text("Были ли сны?", reply_markup=yes_no_kb)
    await state.set_state(SleepSurvey.had_dreams)

@router.callback_query(SleepSurvey.had_dreams, F.data.in_({"yes", "no"}))
async def process_dreams(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "yes":
        # next вопрос
        await state.update_data(had_dreams=(callback.data == "yes"))
        await callback.message.edit_text("Опишите что вам снилось:", reply_markup=back_to_menu)
        await state.set_state(SleepSurvey.dream_content)
    else:
        # next вопрос
        await state.update_data(had_dreams=(callback.data == "no"))
        await callback.message.edit_text("Просыпались ли вы среди ночи?", reply_markup=yes_no_kb)
        await state.set_state(SleepSurvey.woke_up)

@router.message(SleepSurvey.dream_content, F.text)
async def process_dream_content(message: Message, state: FSMContext):
    await state.update_data(dream_content=message.text)
    await message.answer("Просыпались ли вы среди ночи?", reply_markup=yes_no_kb)
    await state.set_state(SleepSurvey.woke_up)

@router.callback_query(SleepSurvey.woke_up, F.data.in_({"yes", "no"}))
async def process_woke_up(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(woke_up=(callback.data == "yes"))
    # next вопрос
    await callback.message.edit_text("Есть ли сейчас усталость или желание поспать?", reply_markup=yes_no_kb)
    await state.set_state(SleepSurvey.tired)

@router.callback_query(SleepSurvey.tired, F.data.in_({"yes", "no"}))
async def process_tired(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(tired=(callback.data == "yes"))
    # next вопрос
    await callback.message.edit_text("Сколько часов вы спали этой ночью? (введите число, например: 7.5)", reply_markup=back_to_menu)
    await state.set_state(SleepSurvey.sleep_hours)

@router.message(SleepSurvey.sleep_hours, F.text)
async def process_sleep_hours(message: Message, state: FSMContext):
    try:
        hours = float(message.text)
        if 0 <= hours <= 24:
            # next вопрос
            await state.update_data(sleep_hours=hours)
            await message.answer("Оцените уровень стресса перед сном (0-5):", reply_markup=scale_1_to_5_kb())
            await state.set_state(SleepSurvey.stress_level)
        else:
            # обработка ошибки
            await message.answer("Пожалуйста, введите число от 0 до 24:", reply_markup=back_to_menu)
    except ValueError:
        # обработка ошибки
        await message.answer("Пожалуйста, введите число. Например: 7.5", reply_markup=back_to_menu)

@router.callback_query(SleepSurvey.stress_level, F.data.startswith("scale_"))
async def process_stress_level(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    stress_level = int(callback.data.split("_")[1])
    await state.update_data(stress_level=stress_level)
    # next вопрос
    await callback.message.edit_text("Ели ли вы пищу перед сном?", reply_markup=food_kb)
    await state.set_state(SleepSurvey.food_before_sleep)

@router.callback_query(SleepSurvey.food_before_sleep, F.data.in_({"heavy", "light", "none"}))
async def process_food(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    food_map = {"heavy": "тяжёлую", "light": "лёгкую", "none": "не ел"}
    await state.update_data(food_before_sleep=food_map[callback.data])
    # next вопрос
    await callback.message.edit_text("Во сколько вы легли спать? (введите время в формате ЧЧ:ММ, например 23:45):", reply_markup=back_to_menu)
    await state.set_state(SleepSurvey.sleep_time)

@router.message(SleepSurvey.sleep_time, F.text.regexp(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"))
async def process_sleep_time(message: Message, state: FSMContext):
    await state.update_data(sleep_time=message.text)
    # next вопрос
    await message.answer("Что ещё вы можете дополнить? (Если нечего добавить, напишите 'нет'):", reply_markup=back_to_menu)
    await state.set_state(SleepSurvey.additional_info)

@router.message(SleepSurvey.sleep_time)
async def process_invalid_sleep_time(message: Message):
    await message.answer("Пожалуйста, введите время в правильном формате (ЧЧ:ММ, например 23:45):", reply_markup=back_to_menu)

@router.message(SleepSurvey.additional_info)
async def process_additional_info(message: Message, state: FSMContext):
    if message.text.lower() != 'нет':
        await state.update_data(additional_info=message.text)
    
    # Получаем все собранные данные
    data = await state.get_data()
    
    # Сохраняем данные в базу
    await save_sleep_entry(message.from_user.id, data)
    
    # Генерируем анализ сна
    prompt = get_sleep_analysis_prompt(data)
    analysis = await generate_response(prompt)
    
    await message.answer(f"Анализ вашего сна:\n\n{analysis}", reply_markup=back_to_menu)
    await state.clear()