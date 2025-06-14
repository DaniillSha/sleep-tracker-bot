import logging
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.db_service import disable_notifications, enable_notifications, get_user_notifications
from bot.keyboards import notification_enabled_kb, notification_settings_kb
from bot.states import NotificationSettings

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "notification_settings")
async def show_notification_settings(callback: CallbackQuery):
    # Показывает меню настроек уведомлений
    await callback.answer()
    
    # Получаем текущие настройки уведомлений пользователя
    notifications = await get_user_notifications(callback.from_user.id)
    
    text = (
        "Вы можете включить уведомления от бота, и он будет каждый день "
        "в установленное время писать и предлагать пройти анализ сна."
    )
    
    if notifications and notifications.notifications_enabled:
        # Если уведомления включены, показываем текущее время
        text += f"\n\nТекущее время уведомлений: {notifications.notification_time}"
        await callback.message.edit_text(text, reply_markup=notification_enabled_kb)
    else:
        # Если уведомления выключены, показываем кнопку включения
        await callback.message.edit_text(text, reply_markup=notification_settings_kb)

@router.callback_query(F.data == "enable_notifications")
async def enable_notifications_handler(callback: CallbackQuery, state: FSMContext):
    # Запрашивает время уведомлений у пользователя
    await callback.answer()
    await state.set_state(NotificationSettings.waiting_for_time)
    await callback.message.edit_text(
        "Введите время уведомлений в формате ЧЧ:ММ (например, 08:30):",
        reply_markup=notification_settings_kb
    )

@router.message(NotificationSettings.waiting_for_time)
async def set_notification_time(message: Message, state: FSMContext):
    # Обрабатывает введенное пользователем время
    # Проверяем формат времени (ЧЧ:ММ)
    if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", message.text):
        await message.answer(
            "Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30):",
            reply_markup=notification_settings_kb
        )
        return
    
    try:
        # Сохраняем настройки в базу данных
        await enable_notifications(message.from_user.id, message.text)
        logger.info(f"Настройки уведомлений сохранены для пользователя {message.from_user.id}: время={message.text}")
        
        # Показываем подтверждение
        await message.answer(
            f"Уведомления включены!\nВы будете получать напоминания каждый день в {message.text}",
            reply_markup=notification_enabled_kb
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при сохранении настроек уведомлений: {e}")
        await message.answer(
            "Произошла ошибка при настройке уведомлений. Попробуйте позже.",
            reply_markup=notification_settings_kb
        )

@router.callback_query(F.data == "disable_notifications")
async def disable_notifications_handler(callback: CallbackQuery):
    # Отключает уведомления
    await callback.answer()
    
    try:
        # Отключаем уведомления в базе данных
        await disable_notifications(callback.from_user.id)
        logger.info(f"Уведомления отключены для пользователя {callback.from_user.id}")
        
        # Показываем подтверждение
        await callback.message.edit_text(
            "Уведомления отключены!",
            reply_markup=notification_settings_kb
        )
    except Exception as e:
        logger.error(f"Ошибка при отключении уведомлений: {e}")
        await callback.message.edit_text(
            "Произошла ошибка при отключении уведомлений. Попробуйте позже.",
            reply_markup=notification_settings_kb
        ) 
