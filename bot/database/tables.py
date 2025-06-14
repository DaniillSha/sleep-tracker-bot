import datetime
from datetime import timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from bot.database.connect import Base

class User(Base):
    # Модель пользователя
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    sleep_entries = relationship("SleepEntry", back_populates="user")
    notifications_enabled = Column(Boolean, default=False)
    notification_time = Column(String(5), nullable=True)  # Формат "HH:MM"
    timezone_offset = Column(Integer, default=0)  # Смещение относительно МСК в часах


class SleepEntry(Base):
    # Модель записи о сне
    __tablename__ = "sleep_entries"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)

    date = Column(Date, default=datetime.date.today)

    feeling_score = Column(Integer)  # Оценка самочувствия
    had_dreams = Column(Boolean)  # Наличие снов
    dream_text = Column(Text)  # Описание снов

    woke_up = Column(Boolean)  # Пробуждения
    tired = Column(Boolean)  # Усталость

    sleep_hours = Column(Float)  # Часы сна
    stress_score = Column(Integer)  # Уровень стресса

    food_type = Column(String)  # Тип пищи перед сном
    sleep_time = Column(Time)  # Время сна
    extra_notes = Column(Text)  # Дополнительные заметки

    user = relationship("User", back_populates="sleep_entries")