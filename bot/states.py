from aiogram.fsm.state import State, StatesGroup

class MainMenu(StatesGroup):
    menu = State()

class SleepSurvey(StatesGroup):
    feeling = State()
    had_dreams = State()
    dream_content = State()
    woke_up = State()
    tired = State()
    sleep_hours = State()
    stress_level = State()
    food_before_sleep = State()
    sleep_time = State()
    additional_info = State()

class NotificationSettings(StatesGroup):
    waiting_for_time = State()

class UserSetup(StatesGroup):
    waiting_for_timezone = State()
