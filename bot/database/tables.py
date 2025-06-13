import datetime
from datetime import timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, ForeignKey, Text, BigInteger, DateTime
from sqlalchemy.orm import relationship
from bot.database.connect import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    sleep_entries = relationship("SleepEntry", back_populates="user")
    notifications_enabled = Column(Boolean, default=False)
    notification_time = Column(String(5), nullable=True)  # Формат "HH:MM"
    timezone_offset = Column(Integer, default=0)  # Смещение относительно МСК в часах


class SleepEntry(Base):
    __tablename__ = "sleep_entries"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)

    date = Column(Date, default=datetime.date.today)

    feeling_score = Column(Integer)
    had_dreams = Column(Boolean)
    dream_text = Column(Text)

    woke_up = Column(Boolean)
    tired = Column(Boolean)

    sleep_hours = Column(Float)
    stress_score = Column(Integer)

    food_type = Column(String)
    sleep_time = Column(Time)
    extra_notes = Column(Text)

    user = relationship("User", back_populates="sleep_entries")