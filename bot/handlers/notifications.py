from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from bot.keyboards import notification_settings_kb, notification_enabled_kb
from bot.database.db_service import get_user_notifications, enable_notifications, disable_notifications
from bot.states import NotificationSettings
import logging
import re

logger = logging.getLogger(__name__)
router = Router()

    #bot/handlers/notifications.py
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

    #bot/handlers/notifications.py
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
            "❌ Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30):",
            reply_markup=notification_settings_kb
        )
        return
    
    try:
        # Сохраняем настройки в базу данных
        await enable_notifications(message.from_user.id, message.text)
        logger.info(f"Notification settings saved for user {message.from_user.id}: time={message.text}")
        
        # Показываем подтверждение
        await message.answer(
            f"✅ Уведомления включены!\nВы будете получать напоминания каждый день в {message.text}",
            reply_markup=notification_enabled_kb
        )
        await state.clear()
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при настройке уведомлений. Попробуйте позже.",
            reply_markup=notification_settings_kb
        )
    #bot/handlers/notifications.py
@router.callback_query(F.data == "disable_notifications")
async def disable_notifications_handler(callback: CallbackQuery):
    # Отключает уведомления
    await callback.answer()
    
    try:
        # Отключаем уведомления в базе данных
        await disable_notifications(callback.from_user.id)
        
        # Показываем подтверждение
        await callback.message.edit_text(
            "✅ Уведомления отключены!",
            reply_markup=notification_settings_kb
        )
    except Exception as e:
        await callback.message.edit_text(
            "❌ Произошла ошибка при отключении уведомлений. Попробуйте позже.",
            reply_markup=notification_settings_kb
        ) 
