import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from bot.ai.generator import generate_response
from bot.ai.prompts import format_sleep_recommendation_prompt
from .sleep_visualization import create_sleep_visualizations

logger = logging.getLogger(__name__)

async def calculate_sleep_stats(df: pd.DataFrame) -> Dict:
    # Расчет статистики сна
    try:
        # Базовые метрики
        total_days = 30
        complete_records = len(df.dropna(subset=['feeling_score', 'sleep_hours', 'stress_score', 'food_type', 'sleep_time']))
        complete_percentage = round((complete_records / total_days) * 100)
        
        # Средние значения
        avg_feeling = round(df['feeling_score'].mean(), 1)
        avg_sleep = round(df['sleep_hours'].mean(), 1)
        avg_stress = round(df['stress_score'].mean(), 1)
        
        # Проценты
        tired_percentage = round((df['tired'].sum() / len(df)) * 100)
        wake_up_percentage = round((df['woke_up'].sum() / len(df)) * 100)
        dreams_percentage = round((df['had_dreams'].sum() / len(df)) * 100)
        
        # Анализ еды
        food_counts = df['food_type'].value_counts()
        most_common_food = food_counts.index[0] if not food_counts.empty else "нет данных"
        
        # Анализ времени сна
        try:
            bedtimes = pd.to_datetime(df['sleep_time'].astype(str), format='%H:%M:%S').dt.time
            total_minutes = sum(t.hour * 60 + t.minute for t in bedtimes)
            avg_minutes = total_minutes / len(bedtimes)
            avg_hours = avg_minutes // 60
            avg_mins = int(avg_minutes % 60)
            avg_bedtime = f"{int(avg_hours):02d}:{avg_mins:02d}"
        except Exception as e:
            logger.error(f"Ошибка при анализе времени сна: {e}")
            avg_bedtime = "нет данных"
        
        # Корреляции
        try:
            stress_feeling_corr = round(stats.pearsonr(df['stress_score'], df['feeling_score'])[0], 2)
        except Exception as e:
            logger.error(f"Ошибка при расчете корреляции стресс-самочувствие: {e}")
            stress_feeling_corr = 0.0
        
        try:
            food_dummies = pd.get_dummies(df['food_type'])
            if 'тяжёлая' in food_dummies.columns:
                food_wake_corr = round(stats.pearsonr(
                    food_dummies['тяжёлая'],
                    df['woke_up'].astype(int)
                )[0], 2)
            else:
                food_wake_corr = 0.0
        except Exception as e:
            logger.error(f"Ошибка при расчете корреляции еда-пробуждения: {e}")
            food_wake_corr = 0.0
        
        # Создаем визуализации
        try:
            plot1_path, plot2_path = create_sleep_visualizations(df)
        except Exception as e:
            logger.error(f"Ошибка при создании визуализаций: {e}")
            plot1_path = None
            plot2_path = None
        
        # Формируем статистику
        stats_dict = {
            'complete_records': complete_records,
            'complete_percentage': complete_percentage,
            'avg_feeling': avg_feeling,
            'avg_sleep': avg_sleep,
            'tired_percentage': tired_percentage,
            'wake_up_percentage': wake_up_percentage,
            'avg_stress': avg_stress,
            'most_common_food': most_common_food,
            'avg_bedtime': avg_bedtime,
            'dreams_percentage': dreams_percentage,
            'stress_feeling_corr': stress_feeling_corr,
            'food_wake_corr': food_wake_corr,
            'plot1_path': plot1_path,
            'plot2_path': plot2_path
        }
        
        # Генерация рекомендации через существующую функцию
        try:
            prompt = format_sleep_recommendation_prompt(stats_dict)
            recommendation = await generate_response(prompt)
        except Exception as e:
            logger.error(f"Ошибка при генерации рекомендации: {e}")
            recommendation = "Продолжайте вести дневник сна для отслеживания своих привычек"
        
        stats_dict['recommendation'] = recommendation
        return stats_dict
        
    except Exception as e:
        logger.error(f"Ошибка в calculate_sleep_stats: {e}")
        raise

def format_stats_message(stats: Dict) -> str:
    # Форматирование статистики в сообщение для Telegram
    try:
        message = [
            "📊 Статистика сна за последний месяц:\n",
            f"📅 Дней с полной записью: {stats['complete_records']} из 30",
            f"📊 Среднее самочувствие утром: {stats['avg_feeling']} из 10",
            f"🛏 Средняя продолжительность сна: {stats['avg_sleep']} часов",
            f"😴 Дней с усталостью по утрам: {stats['tired_percentage']}%",
            f"🌙 Ночных пробуждений: {stats['wake_up_percentage']}%",
            f"🧠 Средний уровень стресса перед сном: {stats['avg_stress']} из 10",
            f"🍽 Чаще всего ел перед сном: {stats['most_common_food']}",
            f"🕐 Среднее время отхода ко сну: {stats['avg_bedtime']}",
            f"💭 Сны были в {stats['dreams_percentage']}% ночей",
            f"📉 Корреляция 'Стресс → Самочувствие': {stats['stress_feeling_corr']}",
            f"🔁 Корреляция 'Еда → Пробуждения ночью': {stats['food_wake_corr']}\n",
            f"📌 Рекомендация: {stats['recommendation']}"
        ]
        
        return "\n".join(message)
    except Exception as e:
        logger.error(f"Ошибка при форматировании статистики: {e}")
        return "Произошла ошибка при формировании статистики. Пожалуйста, попробуйте позже." 