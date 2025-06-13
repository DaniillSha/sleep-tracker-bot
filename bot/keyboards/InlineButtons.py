from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛌 Анализ сна", callback_data="sleep_analysis")],
        [InlineKeyboardButton(text="⏰ Настройка уведомления", callback_data="notification_settings")],
        [InlineKeyboardButton(text="📅 История сна", callback_data="sleep_analysis")],
        [InlineKeyboardButton(text="📊 Получить аналитику сна", callback_data="get_stat")]
    ]
)

analyze_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛌 Анализ сна", callback_data="sleep_analysis")]
    ]
)

def scale_1_to_10_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(1, 6)],
        [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(6, 11)]
    ])

def scale_1_to_5_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(0, 3)],
        [InlineKeyboardButton(text=str(i), callback_data=f"scale_{i}") for i in range(3, 6)]
    ])

yes_no_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Да", callback_data="yes"),
        InlineKeyboardButton(text="Нет", callback_data="no")
    ]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
])

food_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Тяжёлая пища", callback_data="heavy")],
        [InlineKeyboardButton(text="Лёгкая пища", callback_data="light")],
        [InlineKeyboardButton(text="Не ел", callback_data="none")]
])

back_to_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📲 В меню", callback_data="show_main_menu")]
])

notification_settings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Включить уведомления", callback_data="enable_notifications")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="show_main_menu")]
    ]
)


notification_enabled_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=f"🚫 Отключить уведомления", callback_data="disable_notifications")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="show_main_menu")]
    ]
)

def timezone_kb() -> InlineKeyboardMarkup:
    """Клавиатура для выбора часового пояса относительно МСК"""
    keyboard = [
        [
            InlineKeyboardButton(text="МСК-8", callback_data="tz_-8"),
            InlineKeyboardButton(text="МСК-7", callback_data="tz_-7"),
            InlineKeyboardButton(text="МСК-6", callback_data="tz_-6"),
        ],
        [
            InlineKeyboardButton(text="МСК-5", callback_data="tz_-5"),
            InlineKeyboardButton(text="МСК-4", callback_data="tz_-4"),
            InlineKeyboardButton(text="МСК-3", callback_data="tz_-3"),
        ],
        [
            InlineKeyboardButton(text="МСК-2", callback_data="tz_-2"),
            InlineKeyboardButton(text="МСК-1", callback_data="tz_-1"),
            InlineKeyboardButton(text="МСК+0", callback_data="tz_0"),
        ],
        [
            InlineKeyboardButton(text="МСК+1", callback_data="tz_1"),
            InlineKeyboardButton(text="МСК+2", callback_data="tz_2"),
            InlineKeyboardButton(text="МСК+3", callback_data="tz_3"),
        ],
        [
            InlineKeyboardButton(text="МСК+4", callback_data="tz_4"),
            InlineKeyboardButton(text="МСК+5", callback_data="tz_5"),
            InlineKeyboardButton(text="МСК+6", callback_data="tz_6"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)