import os
from datetime import datetime
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.database.db_service import get_sleep_entries_for_month
from bot.ai.sleep_stats import calculate_sleep_stats, format_stats_message
from bot.ai.sleep_visualization import create_sleep_visualizations
from bot.keyboards import back_to_menu
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "get_stat")
async def handle_get_stat(callback: CallbackQuery, session: AsyncSession):
    """Обработчик запроса анализа сна"""
    try:
        # Сразу отвечаем на callback, чтобы избежать таймаута
        await callback.answer()
        
        # Отправляем промежуточное сообщение
        status_message = await callback.message.answer("📊 Анализирую ваши данные о сне...")
        
        # Получаем данные о сне за последний месяц
        sleep_entries = await get_sleep_entries_for_month(callback.from_user.id)
        
        if not sleep_entries:
            await status_message.edit_text("Для статистики нужны записи хотя-бы за 30 дней :(")
            return
        
        # Преобразуем записи в DataFrame
        df = pd.DataFrame([{
            'feeling_score': entry.feeling_score,
            'sleep_hours': entry.sleep_hours,
            'stress_score': entry.stress_score,
            'food_type': entry.food_type,
            'sleep_time': entry.sleep_time,
            'tired': entry.tired,
            'woke_up': entry.woke_up,
            'had_dreams': entry.had_dreams
        } for entry in sleep_entries])
        
        # Генерируем статистику
        stats = await calculate_sleep_stats(df)
        stats_message = format_stats_message(stats)
        
        # Формируем финальное сообщение
        user_name = callback.from_user.first_name
        final_message = (
            f"*{user_name}*!\n\n"
            f"Мы проанализировали твои данные о сне за последние 30 дней и подготовили краткий отчёт с нейроанализом:\n\n"
            f"{stats_message}\n\n"
            f"💡 Хочешь получить полный отчёт с детальным анализом и рекомендациями? "
            f"Нажми на кнопку ниже 👇"
        )
        
        # Обновляем сообщение со статистикой
        await status_message.edit_text(final_message, parse_mode="Markdown", reply_markup=back_to_menu)
        
        # Генерируем графики
        try:
            logger.info("Starting plots generation...")
            plot1_path, plot2_path = create_sleep_visualizations(df)
            logger.info(f"Plots generated at paths: {plot1_path}, {plot2_path}")
            
            # Отправляем графики
            if plot1_path and os.path.exists(plot1_path):
                logger.info("Sending first plot...")
                await callback.message.answer_photo(
                    types.FSInputFile(plot1_path),
                    caption="📊 Распределение продолжительности сна по категориям"
                )
                logger.info("First plot sent successfully")
            
            if plot2_path and os.path.exists(plot2_path):
                logger.info("Sending second plot...")
                await callback.message.answer_photo(
                    types.FSInputFile(plot2_path),
                    caption="📈 Тренд продолжительности сна и самочувствия"
                )
                logger.info("Second plot sent successfully")
                
        except Exception as e:
            logger.error(f"Произошла ошибка при генерации графиков: {e}", exc_info=True)
            
    except Exception as e:
        logger.error(f"Произошла ошибка при анализе сна: {e}")
        await callback.message.answer("Произошла ошибка при анализе сна. Попробуйте позже.")